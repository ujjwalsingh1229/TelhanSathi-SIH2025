// ==========================================
// CONSENSUS MODULE - Proof of Authority (PoA)
// ==========================================

class Consensus {
    constructor(nodeRegistry) {
        this.nodeRegistry = nodeRegistry;
        this.consensusType = 'PoA'; // Proof of Authority
        this.blockValidationThreshold = 0.51; // 51% of validators must agree
    }

    // Validate if a node can create a block (only validators can)
    canCreateBlock(nodeId) {
        return this.nodeRegistry.isValidator(nodeId);
    }

    // Select next validator (round-robin among active validators)
    selectNextValidator(lastValidatorId = null) {
        const validators = this.nodeRegistry.getValidators();

        if (validators.length === 0) {
            return null;
        }

        if (validators.length === 1) {
            return validators[0].nodeId;
        }

        if (!lastValidatorId) {
            // Return first validator
            return validators[0].nodeId;
        }

        // Find current validator index
        const currentIndex = validators.findIndex(v => v.nodeId === lastValidatorId);

        // Select next validator (round-robin)
        const nextIndex = (currentIndex + 1) % validators.length;
        return validators[nextIndex].nodeId;
    }

    // Validate block signature (simplified - in production use proper crypto signatures)
    validateBlockSignature(block, validatorId) {
        // In a real implementation, validate cryptographic signature
        // For now, just check if the block creator is a validator
        return this.nodeRegistry.isValidator(validatorId);
    }

    // Validate new block from network
    validateNewBlock(block, previousBlock, fromNode) {
        const validations = [];

        // 1. Check if sender is a validator
        if (!this.nodeRegistry.isValidator(fromNode)) {
            validations.push({
                valid: false,
                rule: 'VALIDATOR_CHECK',
                message: 'Block creator is not a validator'
            });
        } else {
            validations.push({
                valid: true,
                rule: 'VALIDATOR_CHECK',
                message: 'Block creator is a valid validator'
            });
        }

        // 2. Check block index
        if (block.index !== previousBlock.index + 1) {
            validations.push({
                valid: false,
                rule: 'INDEX_CHECK',
                message: 'Invalid block index'
            });
        } else {
            validations.push({
                valid: true,
                rule: 'INDEX_CHECK',
                message: 'Block index is correct'
            });
        }

        // 3. Check previous hash linkage
        if (block.previousHash !== previousBlock.hash) {
            validations.push({
                valid: false,
                rule: 'PREVIOUS_HASH_CHECK',
                message: 'Previous hash mismatch'
            });
        } else {
            validations.push({
                valid: true,
                rule: 'PREVIOUS_HASH_CHECK',
                message: 'Previous hash is correct'
            });
        }

        // 4. Check block hash validity
        const crypto = require('crypto');
        const stringify = require('fast-json-stable-stringify');
        const hashInput = `${block.index}${block.previousHash}${block.timestamp}${stringify(block.data)}${block.nonce}${block.merkleRoot}`;
        const calculatedHash = crypto.createHash('sha256').update(hashInput).digest('hex');

        if (block.hash !== calculatedHash) {
            validations.push({
                valid: false,
                rule: 'HASH_CHECK',
                message: 'Block hash is invalid'
            });
        } else {
            validations.push({
                valid: true,
                rule: 'HASH_CHECK',
                message: 'Block hash is valid'
            });
        }

        // 5. Check merkle root
        const merkleRoot = crypto.createHash('sha256').update(stringify(block.data)).digest('hex');
        if (block.merkleRoot !== merkleRoot) {
            validations.push({
                valid: false,
                rule: 'MERKLE_ROOT_CHECK',
                message: 'Merkle root is invalid'
            });
        } else {
            validations.push({
                valid: true,
                rule: 'MERKLE_ROOT_CHECK',
                message: 'Merkle root is valid'
            });
        }

        // 6. Check timestamp (not in the future, not too old)
        const now = Date.now();
        const blockAge = now - block.timestamp;
        if (block.timestamp > now + 60000) { // 1 minute future tolerance
            validations.push({
                valid: false,
                rule: 'TIMESTAMP_CHECK',
                message: 'Block timestamp is in the future'
            });
        } else if (blockAge > 3600000) { // 1 hour old
            validations.push({
                valid: false,
                rule: 'TIMESTAMP_CHECK',
                message: 'Block is too old'
            });
        } else {
            validations.push({
                valid: true,
                rule: 'TIMESTAMP_CHECK',
                message: 'Block timestamp is valid'
            });
        }

        const allValid = validations.every(v => v.valid);

        return {
            isValid: allValid,
            validations,
            validatorId: fromNode
        };
    }

    // Resolve chain conflicts (longest chain rule with reputation-based tiebreaker)
    resolveConflict(localChain, remoteChain, remoteNodeId) {
        // 1. Check if remote node is trusted
        const isTrustedNode = this.nodeRegistry.isValidator(remoteNodeId) ||
            this.nodeRegistry.isActive(remoteNodeId);

        if (!isTrustedNode) {
            return {
                shouldReplace: false,
                reason: 'Remote node is not trusted'
            };
        }

        // 2. Check chain length
        if (remoteChain.length < localChain.length) {
            return {
                shouldReplace: false,
                reason: 'Remote chain is shorter than local chain'
            };
        }

        // 3. Validate remote chain integrity
        if (!this.validateChainIntegrity(remoteChain)) {
            return {
                shouldReplace: false,
                reason: 'Remote chain integrity check failed'
            };
        }

        // 4. Check if remote chain has more validator-created blocks
        const localValidatorBlocks = this.countValidatorBlocks(localChain);
        const remoteValidatorBlocks = this.countValidatorBlocks(remoteChain);

        if (remoteValidatorBlocks < localValidatorBlocks) {
            return {
                shouldReplace: false,
                reason: 'Remote chain has fewer validator blocks'
            };
        }

        // 5. Handle equal length chains (split-brain recovery)
        if (remoteChain.length === localChain.length) {
            // Tiebreaker: Use validator reputation score
            const remoteLastValidator = remoteChain[remoteChain.length - 1].validatorId;
            const localLastValidator = localChain[localChain.length - 1].validatorId;

            const remoteValidatorRep = this.nodeRegistry.getReputation(remoteLastValidator) || 0;
            const localValidatorRep = this.nodeRegistry.getReputation(localLastValidator) || 0;

            if (remoteValidatorRep > localValidatorRep) {
                return {
                    shouldReplace: true,
                    reason: 'Equal length chains - remote validator has higher reputation',
                    lengthDiff: 0,
                    tiebreaker: 'validator_reputation',
                    remoteReputation: remoteValidatorRep,
                    localReputation: localValidatorRep
                };
            } else if (remoteValidatorRep < localValidatorRep) {
                return {
                    shouldReplace: false,
                    reason: 'Equal length chains - local validator has higher reputation',
                    lengthDiff: 0,
                    tiebreaker: 'validator_reputation',
                    remoteReputation: remoteValidatorRep,
                    localReputation: localValidatorRep
                };
            }

            // Reputation is equal - use timestamp tiebreaker
            const remoteBlockTime = remoteChain[remoteChain.length - 1].timestamp;
            const localBlockTime = localChain[localChain.length - 1].timestamp;

            if (remoteBlockTime < localBlockTime) {
                return {
                    shouldReplace: true,
                    reason: 'Equal length and reputation - remote chain created first',
                    lengthDiff: 0,
                    tiebreaker: 'block_timestamp',
                    remoteTime: remoteBlockTime,
                    localTime: localBlockTime
                };
            }

            return {
                shouldReplace: false,
                reason: 'Equal length, reputation and timestamp - keeping local chain',
                lengthDiff: 0,
                tiebreaker: 'timestamp_equal'
            };
        }

        // Remote chain is longer
        return {
            shouldReplace: true,
            reason: 'Remote chain is longer and valid',
            lengthDiff: remoteChain.length - localChain.length,
            validatorBlockDiff: remoteValidatorBlocks - localValidatorBlocks
        };
    }

    // Validate entire chain integrity
    validateChainIntegrity(chain) {
        for (let i = 1; i < chain.length; i++) {
            const currentBlock = chain[i];
            const previousBlock = chain[i - 1];

            // Check hash linkage
            if (currentBlock.previousHash !== previousBlock.hash) {
                return false;
            }

            // Validate hash
            const crypto = require('crypto');
            const stringify = require('fast-json-stable-stringify');
            const hashInput = `${currentBlock.index}${currentBlock.previousHash}${currentBlock.timestamp}${stringify(currentBlock.data)}${currentBlock.nonce}${currentBlock.merkleRoot}`;
            const calculatedHash = crypto.createHash('sha256').update(hashInput).digest('hex');

            if (currentBlock.hash !== calculatedHash) {
                return false;
            }
        }

        return true;
    }

    // Count blocks created by validators
    countValidatorBlocks(chain) {
        let count = 0;
        for (const block of chain) {
            if (block.data.validatorId && this.nodeRegistry.isValidator(block.data.validatorId)) {
                count++;
            }
        }
        return count;
    }

    // Penalize misbehaving node
    penalizeNode(nodeId, reason, severity = 'medium') {
        const penalties = {
            'low': -5,
            'medium': -15,
            'high': -30,
            'critical': -50
        };

        const reputationChange = penalties[severity] || penalties.medium;
        const result = this.nodeRegistry.updateReputation(nodeId, reputationChange, reason);

        console.log(`⚠️  Node ${nodeId} penalized: ${reason} (${severity})`);

        // If reputation too low, consider removing node
        if (result.reputation < 10) {
            console.log(`🚫 Node ${nodeId} has critically low reputation, consider removal`);
        }

        return result;
    }

    // Reward well-behaving node
    rewardNode(nodeId, reason) {
        const result = this.nodeRegistry.updateReputation(nodeId, 2, reason);
        return result;
    }

    // Get consensus statistics
    getStats() {
        return {
            consensusType: this.consensusType,
            totalValidators: this.nodeRegistry.getValidators().length,
            validationThreshold: this.blockValidationThreshold,
            activeNodes: this.nodeRegistry.getActiveNodes().length
        };
    }
}

module.exports = Consensus;
