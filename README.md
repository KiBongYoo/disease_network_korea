# Disease Network in Korea 한국 질병 네트워크(updated 2026.5.31.)
Information and codes for disease network in Korea
이 페이지는 한국 국민건강보험공단의 건강보험 빅데이터를 이용하여 개발한 질병 진행 네트워크에 대한 기초 정보 및 이용 코드를 공유하기 위해 생성된 github이다.

폴더 구분은 
1. Disease_information(질병 그룹 목록 파일)
2. Disease_progression_network(질병 진행 네트워크 데이터셋)
- OUTPUT_UNI_M_HLT_ALL.csv : Contains the resulting edge weights for the transitions from a healthy state (no disease) to subsequent diseases in men.
- OUTPUT_UNI_W_HLT_ALL.csv : Contains the resulting edge weights for the transitions from a healthy state (no disease) to subsequent diseases in women.

- OUTPUT_UNI_M_ALL_Q_FILTERED.csv : Filtered univariate edge weights for men cohorts, capturing inter-layer and intra-layer relationships from precedent to subsequent diseases.
- OUTPUT_UNI_W_ALL_Q_FILTERED.csv : Filtered univariate edge weights for women cohorts, capturing inter-layer and intra-layer relationships from precedent to subsequent diseases.

- output_m_step1_q_filtered.csv : Filtered 1st IPW edge weights for men cohorts, capturing intra-layer relationships from precedent to subsequent diseases.
- output_w_step1_q_filtered.csv : Filtered 1st IPW edge weights for women cohorts, capturing intra-layer relationships from precedent to subsequent diseases.


The files will be updated regularly.
지속적으로 업데이트할 예정이다.

!(https://github.com/KiBongYoo/disease_network_korea/blob/main/NetSci2026%20poster.png)
