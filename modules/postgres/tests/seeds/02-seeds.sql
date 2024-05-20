-- Sample data, to be loaded after the schema
INSERT INTO stuff (name)
VALUES ('foo'), ('bar'), ('qux'), ('frob')
RETURNING id;
