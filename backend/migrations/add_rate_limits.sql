-- Rate limits tracking table
CREATE TABLE IF NOT EXISTS rate_limits (
  date DATE PRIMARY KEY,
  request_count INTEGER DEFAULT 0 NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Update updated_at automatically
CREATE OR REPLACE FUNCTION update_rate_limits_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = timezone('utc'::text, now());
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER rate_limits_updated_at_trigger
BEFORE UPDATE ON rate_limits
FOR EACH ROW
EXECUTE FUNCTION update_rate_limits_updated_at();
