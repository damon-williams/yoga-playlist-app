-- Add user_id and is_public columns to support user-specific custom classes
ALTER TABLE yoga_class_types 
ADD COLUMN user_id VARCHAR(255) NULL,
ADD COLUMN is_public BOOLEAN DEFAULT false;

-- Make all existing classes public (these are the core yoga types)
UPDATE yoga_class_types 
SET is_public = true 
WHERE user_id IS NULL;

-- Add index for performance when filtering by user_id
CREATE INDEX idx_yoga_class_types_user_id ON yoga_class_types(user_id);
CREATE INDEX idx_yoga_class_types_public ON yoga_class_types(is_public);

-- Example query that will be used:
-- SELECT * FROM yoga_class_types 
-- WHERE is_public = true 
--    OR user_id = 'fairydust_user_id_here'
-- ORDER BY is_public DESC, created_at ASC;