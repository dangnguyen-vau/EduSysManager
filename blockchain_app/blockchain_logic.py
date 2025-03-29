import hashlib
import json
from .models import Block, Transaction
from django.utils import timezone

class BlockchainManager:
    @staticmethod
    def calculate_hash(index, previous_hash, timestamp, merkle_root, nonce):
        data = f"{index}{previous_hash}{timestamp.timestamp()}{merkle_root}{nonce}"
        return hashlib.sha256(data.encode()).hexdigest()

    @staticmethod
    def calculate_merkle_root(transactions):
        if not transactions:
            return hashlib.sha256("0".encode()).hexdigest()

        transaction_hashes = []
        for tx in transactions:
            tx_data = {
                'transaction_id': str(tx.transaction_id),
                'student': tx.student.student_id,
                'course': tx.course.code,
                'score': tx.score,
                'status': tx.status,
                'timestamp': tx.timestamp.timestamp()
            }
            if tx.approved_by:
                tx_data['approved_by'] = tx.approved_by.username
                tx_data['approval_time'] = tx.approval_time.timestamp() if tx.approval_time else None
            
            tx_hash = hashlib.sha256(json.dumps(tx_data, sort_keys=True).encode()).hexdigest()
            transaction_hashes.append(tx_hash)

        while len(transaction_hashes) > 1:
            temp_hashes = []
            for i in range(0, len(transaction_hashes), 2):
                if i + 1 == len(transaction_hashes):
                    temp_hashes.append(transaction_hashes[i])
                else:
                    combined = transaction_hashes[i] + transaction_hashes[i + 1]
                    temp_hashes.append(hashlib.sha256(combined.encode()).hexdigest())
            transaction_hashes = temp_hashes

        return transaction_hashes[0]

    @staticmethod
    def mine_block(index, transactions, previous_hash, difficulty=4):
        nonce = 0
        timestamp = timezone.now()
        merkle_root = BlockchainManager.calculate_merkle_root(transactions)
        target = "0" * difficulty

        # Mine the block to find nonce and hash
        while True:
            hash = BlockchainManager.calculate_hash(index, previous_hash, timestamp, merkle_root, nonce)
            if hash.startswith(target):
                break
            nonce += 1

        # Create block with all values
        block = Block.objects.create(
            index=index,
            hash=hash,
            previous_hash=previous_hash,
            merkle_root=merkle_root,
            timestamp=timestamp,
            nonce=nonce,
            difficulty=difficulty
        )
        
        # Add transactions to the block
        block.transactions.set(transactions)
        block.save()
        
        return block

    @staticmethod
    def verify_chain():
        blocks = Block.objects.all().order_by('index')
        
        # Nếu không có block nào, blockchain hợp lệ
        if not blocks:
            return True, "Blockchain is empty but valid"
            
        # Nếu chỉ có 1 block (genesis block), kiểm tra previous_hash phải là '0'
        if len(blocks) == 1:
            if blocks[0].previous_hash == '0':
                return True, "Blockchain is valid"
            return False, "Invalid genesis block"

        # Kiểm tra tính liên kết của các block
        for i in range(1, len(blocks)):
            current_block = blocks[i]
            previous_block = blocks[i-1]

            # Chỉ kiểm tra previous hash
            if current_block.previous_hash != previous_block.hash:
                return False, f"Block #{current_block.index} không liên kết với block trước đó"

        return True, "Blockchain hợp lệ"

    @staticmethod
    def get_pending_transactions():
        return Transaction.objects.filter(status='pending', is_mined=False)
        
    @staticmethod
    def get_approved_unmined_transactions():
        return Transaction.objects.filter(status='approved', is_mined=False) 