"""Generate Mermaid knowledge graph from concept relationships."""

import os


def generate_graph(analysis: dict, output_dir: str) -> str:
    """Generate a Mermaid mindmap/graph of all concepts."""
    mermaid = "```mermaid\ngraph TD\n"

    node_id = 0
    nodes = {}
    edges = []

    for ch in analysis.get("chapters", []):
        ch_id = f"N{node_id}"
        node_id += 1
        nodes[ch_id] = f"第{ch['order']}章: {ch['title']}"

        for sec in ch.get("sections", []):
            sec_id = f"N{node_id}"
            node_id += 1
            nodes[sec_id] = sec["title"]
            edges.append((ch_id, sec_id))

            for c in sec.get("concepts", []):
                c_id = f"N{node_id}"
                node_id += 1
                nodes[c_id] = c["name"]
                edges.append((sec_id, c_id))

    for nid, label in nodes.items():
        escaped = label.replace('"', '\\"')
        mermaid += f'    {nid}["{escaped}"]\n'

    for src, dst in edges:
        mermaid += f"    {src} --> {dst}\n"

    for ch in analysis.get("chapters", []):
        for sec in ch.get("sections", []):
            for c in sec.get("concepts", []):
                for related in c.get("related_concepts", []):
                    target_id = None
                    for nid, label in nodes.items():
                        if related in label:
                            target_id = nid
                            break
                    if target_id:
                        source_id = None
                        for nid, label in nodes.items():
                            if c["name"] in label:
                                source_id = nid
                                break
                        if source_id and source_id != target_id:
                            mermaid += f'    {source_id} -.->|"关联"| {target_id}\n'

    mermaid += "```\n"

    os.makedirs(output_dir, exist_ok=True)
    graph_path = os.path.join(output_dir, "knowledge_graph.md")
    with open(graph_path, "w", encoding="utf-8") as f:
        f.write(f"# 知识图谱\n\n{mermaid}")

    return mermaid
