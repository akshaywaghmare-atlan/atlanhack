import prestodb

def test_presto_connection():
    conn = None
    cur = None
    try:
        # Create a connection to Presto
        conn = prestodb.dbapi.connect(
            host='13.127.207.43',
            port=8080,
            user='admin',
            catalog='system',  # Start with system catalog which is always available
            schema='runtime'   # Use runtime schema to check nodes
        )
        
        cur = conn.cursor()
        
        # 1. First check if server is running by querying nodes
        print("\n1. Checking Presto nodes:")
        cur.execute('SELECT node_id, http_uri, node_version FROM system.runtime.nodes')
        nodes = cur.fetchall()
        print(f"Server is running with {len(nodes)} node(s)")
        for node in nodes:
            print(f"Node: {node[0]}, URI: {node[1]}, Version: {node[2]}")

        # 2. List all catalogs
        print("\n2. Available catalogs:")
        cur.execute('SELECT * FROM system.metadata.catalogs')
        catalogs = cur.fetchall()
        print("Catalogs:", [catalog[0] for catalog in catalogs])

        # 3. Try to list schemas from each catalog
        print("\n3. Checking schemas in each catalog:")
        for catalog in catalogs:
            catalog_name = catalog[0]
            try:
                cur.execute(f'SELECT schema_name FROM {catalog_name}.information_schema.schemata')
                schemas = cur.fetchall()
                print(f"\nSchemas in '{catalog_name}' catalog:")
                for schema in schemas:
                    print(f"- {schema[0]}")
            except Exception as e:
                print(f"Could not query schemas in '{catalog_name}': {str(e)}")

    except Exception as e:
        print(f"Connection error: {str(e)}")
    finally:
        try:
            if cur:
                cur.close()
            if conn:
                conn.close()
        except:
            pass

if __name__ == "__main__":
    test_presto_connection() 