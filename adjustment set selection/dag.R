dag_data <- read.csv("C:/Users/user/Downloads/sub_graph.csv")

edges <- apply(dag_data, 1, function(row) paste(row[1], row[2], row[3]))
edges
dag_string <- paste("DAG {", paste(edges, collapse = "; "), "}", sep = "")
dag_string
dag <- dagitty(dag_string)
dag


adjustmentSets(x=dag, exposure="1003", outcome="1005", type="minimal", effect="direct")
adjustmentSets(x=dag, exposure="1003", outcome="1005", type="minimal", effect="total")

