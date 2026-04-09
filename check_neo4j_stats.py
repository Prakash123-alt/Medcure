import asyncio
from medical_ai_agent.knowledge_graph import neo4j_db

async def get_stats():
    driver = await neo4j_db.connect_async()
    async with driver.session() as s:
        r_nodes = await s.run("MATCH (n) RETURN count(n)")
        nodes = (await r_nodes.single())[0]
        r_rels = await s.run("MATCH ()-[r]->() RETURN count(r)")
        rels = (await r_rels.single())[0]
        
        # Check specific types
        r_dis = await s.run("MATCH (n:Disease) RETURN count(n)")
        dis = (await r_dis.single())[0]
        r_dr = await s.run("MATCH (n:Drug) RETURN count(n)")
        dr = (await r_dr.single())[0]
        
        # Check last chunk
        r_last = await s.run("MATCH (c:GuidelineChunk) RETURN c.chunk_id ORDER BY c.chunk_id DESC LIMIT 1")
        last_id = (await r_last.single())[0]
        
        print(f"--- NEO4J CURRENT STATS ---")
        print(f"Total Nodes: {nodes}")
        print(f"Total Relationships: {rels}")
        print(f"Diseases: {dis}")
        print(f"Drugs: {dr}")
        print(f"Last Chunk ID: {last_id}")
    await driver.close()

if __name__ == "__main__":
    asyncio.run(get_stats())
