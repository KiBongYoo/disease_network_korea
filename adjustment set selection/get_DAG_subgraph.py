import pandas as pd
import networkx as nx
import random
from multiprocessing import Pool, cpu_count
import os
from tqdm import tqdm  # 진행률 시각화
import random

# 1. 양방향 엣지 랜덤으로 제거
def remove_direction(graph):
    unique_pairs = set()
    bidirectional_pairs = [(u, v) for u, v in graph.edges() if graph.has_edge(v, u)]

    random_rr_pairs = []
    for u, v in bidirectional_pairs:
        sorted_pair = tuple(sorted([u, v]))
        if sorted_pair not in unique_pairs:
            if random.choice([True, False]):
                random_rr_pairs.append((u, v, graph[u][v]['RR']))
            else:
                random_rr_pairs.append((v, u, graph[v][u]['RR']))
            unique_pairs.add(sorted_pair)

    all_edges = set(graph.edges()) - set(bidirectional_pairs)
    final_edges = [(u, v, graph[u][v]['RR']) for u, v in all_edges] + random_rr_pairs

    graph2 = nx.DiGraph()
    graph2.add_edges_from([(u, v, {'RR': rr}) for u, v, rr in final_edges])

    return graph2

# 1-2(검증용). 양방향 엣지 중 RR이 높은 쌍을 남기기
def remove_direction_2(graph):
    unique_pairs = set()
    bidirectional_pairs = [(u, v) for u, v in graph.edges() if graph.has_edge(v, u)]

    selected_rr_pairs = []
    for u, v in bidirectional_pairs:
        sorted_pair = tuple(sorted([u, v]))
        if sorted_pair not in unique_pairs:
            rr_uv = graph[u][v]['RR']
            rr_vu = graph[v][u]['RR']
            
            # RR 값이 큰 쪽을 남김
            if rr_uv >= rr_vu:
                selected_rr_pairs.append((u, v, rr_uv))
            else:
                selected_rr_pairs.append((v, u, rr_vu))
                
            unique_pairs.add(sorted_pair)

    all_edges = set(graph.edges()) - set(bidirectional_pairs)
    final_edges = [(u, v, graph[u][v]['RR']) for u, v in all_edges] + selected_rr_pairs

    graph2 = nx.DiGraph()
    graph2.add_edges_from([(u, v, {'RR': rr}) for u, v, rr in final_edges])

    return graph2


# 2. 사이클 내 엣지 삭제
def removeEdge(graph, subgraph, cycle, mediator_edges, D1, D2):
    while True:
        idx = random.randint(0, len(cycle) - 2)
        node, next_node = cycle[idx], cycle[idx + 1]
        
        if (node, next_node) in mediator_edges:
            continue
        else:
            if subgraph.has_edge(node, next_node):
                subgraph.remove_edge(node, next_node)
            if graph.has_edge(node, next_node):
                graph.remove_edge(node, next_node)
            break

# 3. 사이클 제거 로직 (최적화)
def remove_cycle(graph, D1, D2):
    all_paths = list(nx.all_simple_paths(graph, D1, D2, cutoff=2))

    unique_nodes = {node for path in all_paths for node in path}
    temp = unique_nodes.copy()
    for node in temp:
        if (int(D1/1000) < int(node/1000) and node != D2) or (int(D1/1000) > int(node/1000)):
            unique_nodes.discard(node)

    mediator_edges = {(path[i], path[i+1]) for path in all_paths for i in range(len(path)-1)}

    neighbors = set(graph.neighbors(D1)).union(graph.predecessors(D1), graph.neighbors(D2), graph.predecessors(D2))
    neighbors = {n for n in neighbors if not ((int(D1/1000) < int(n/1000) and n != D2) or int(D1/1000) > int(n/1000))}

    all_selected_nodes = unique_nodes.union(neighbors, {D1, D2})

    subgraph = graph.subgraph(all_selected_nodes).copy()
    subgraph.remove_edges_from(list(graph.out_edges(D2)))
    subgraph.remove_edge(D2, D1) if subgraph.has_edge(D2, D1) else None
    subgraph = remove_direction(subgraph)

    directed_graph = subgraph.copy()
    for scc in nx.strongly_connected_components(directed_graph):
        if len(scc) < 2:
            continue
        directed_subgraph = directed_graph.subgraph(scc).copy()
        while True:
            try:
                cycle = next(nx.simple_cycles(directed_subgraph))
                removeEdge(directed_graph, directed_subgraph, cycle, mediator_edges, D1, D2)
            except StopIteration:
                break
    return directed_graph

# 4. DAG 방향 문자열로 출력
def export_custom_dag_to_array(subgraph):
    processed_edges = set()
    result = []
    for u, v in subgraph.edges():
        if (u, v) in processed_edges or (v, u) in processed_edges:
            continue
        if subgraph.has_edge(v, u):
            result.append(f"{u} <-> {v}")
            processed_edges.add((u, v))
            processed_edges.add((v, u))
        else:
            result.append(f"{u} -> {v}")
        processed_edges.add((u, v))
    return result

# 5. 프로세스 단위 처리 (병렬화 대상)
def process_pair(args):
    edges, D1, D2 = args
    graph = nx.DiGraph()
    graph.add_edges_from(edges)
    subgraph = remove_cycle(graph, D1, D2)
    edge_directions_str = "{ " + " ".join(export_custom_dag_to_array(subgraph)) + " }"
    print("\n", D1, " ", D2, "\n")
    return [D1, D2, edge_directions_str, None]

# 6. 메인 함수 (병렬 처리 적용)
def main(directory, sex, flag):
    input_file = os.path.join(directory, f'output_{sex}_filtered_ALL_0_flag5.csv')
    df = pd.read_csv(input_file)[['source', 'target', 'RR', 'flag']]

    edges_data = [(int(row.source), int(row.target), {'RR': row.RR, 'Flag': row.flag}) for _, row in df.iterrows()]
    graph = nx.DiGraph()
    graph.add_edges_from(edges_data)

    pairs_to_process = [(edges_data, u, v) for u, v, d in graph.edges(data=True) if d['Flag'] == flag]
    random.shuffle(pairs_to_process)  # 랜덤하게 섞기

    for i in range(10, 12):
        print(f"Starting iteration {i}...")
        with Pool(processes=max(1, cpu_count() - 4)) as pool:
            results = pool.map(process_pair, pairs_to_process)

        result_df = pd.DataFrame(results, columns=["D1", "D2", "Edge Directions", "Confounder2"])
        result_df.to_csv(os.path.join(directory, f'output_{sex}_{flag}_{i}.csv'), index=False)

        temp_df = pd.DataFrame([f"{r[0]}{r[1]}" for r in results], columns=["D1D2"])
        temp_df.to_csv(os.path.join(directory, f'temp_{sex}_{flag}_{i}.csv'), index=False)

        print(f'Iteration {i} completed.')


if __name__ == "__main__":
    directory = 'G:/내 드라이브/research2024/diseasenetwork/반출된 edges/final/' # 데이터가 있는 폴더 경로 입력
    sex = 'w'
    flag = 5
    main(directory, sex, flag)
