#install.packages("callr")
library(callr)      # 별도의 R 프로세스 실행을 위해 필요
library(dagitty)    # DAG 처리
library(R.utils)    # withTimeout 등이 포함된 유틸리티

file_path <- "G:/내 드라이브/research2024/diseasenetwork/반출된 edges/final/null_list.csv"   # 입력 파일 경로
dag_data <- read.csv(file_path)

end <- nrow(dag_data)
records <- list()

for (i in 1:end) {
  D1 <- as.character(dag_data[i, 1])
  D2 <- as.character(dag_data[i, 2])
  message(sprintf("Processing row %d: %s, %s", i, D1, D2))
  
  # 각 행의 계산을 별도의 프로세스에서 실행
  result <- tryCatch({
    # callr::r() 함수로 별도 프로세스 호출, timeout은 240초로 지정
    callr::r(
      function(row_data) {
        # 주의: 독립 프로세스이므로 필요한 라이브러리들을 반드시 load 해야 합니다.
        library(dagitty)
        # 입력된 DAG 문자열 형식 확인 (예: "DAG { ... }")
        dag_string <- paste("DAG ", row_data[3], sep = "")
        dag <- dagitty(dag_string)
        # adjustmentSets 계산
        res <- adjustmentSets(x = dag,
                              exposure = as.character(row_data[1]),
                              outcome = as.character(row_data[2]),
                              type = "minimal",
                              effect = "total")
        return(res)
      },
      args = list(row_data = dag_data[i,]),
      timeout = 10
    )
  }, error = function(e) {
    message(sprintf("Error processing row %d: %s", i, e$message))
    return("time out")
  })
  
  # 결과가 NULL 이면 빈 문자열로, 아니면 가장 짧은 조정변수 집합 선택
  if (is.null(result)) {
    shortest_list_str <- ""
  } else {
    lengths_of_lists <- sapply(result, length)
    min_index <- which.min(lengths_of_lists)
    shortest_list_str <- paste(unlist(result[[min_index]]), collapse = " ")
  }
  
  records[[i]] <- list(D1 = D1, D2 = D2, con_vars = shortest_list_str)
  
  # 진행 중간에 결과 저장 (필요하다면 주석 처리 후 나중에 한 번에 저장해도 됩니다)
  df_intermediate <- do.call(rbind, lapply(records, function(x) {
    data.frame(
      D1 = x$D1,
      D2 = x$D2,
      con_vars = x$con_vars,
      stringsAsFactors = FALSE
    )
  }))
  
  file_name <- basename(file_path)
  file_name_no_ext <- tools::file_path_sans_ext(file_name)
  new_file_name <- paste0(file_name_no_ext, "_con.csv")
  new_file_path <- file.path(dirname(file_path), new_file_name)
  write.csv(df_intermediate, file = new_file_path, row.names = TRUE)
}

# 최종 결과 저장
df <- do.call(rbind, lapply(records, function(x) {
  data.frame(
    D1 = x$D1,
    D2 = x$D2,
    con_vars = x$con_vars,
    stringsAsFactors = FALSE
  )
}))
write.csv(df, file = new_file_path, row.names = TRUE)
