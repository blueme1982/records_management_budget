import pandas as pd
import re

class ProjectClassifier:
    # 프로젝트 타입 키워드 매핑 (우선순위 순)
    PROJECT_TYPE_KEYWORDS = {
        'DIGITALIZATION': [
            '전자화', '디지털화', '스캔', '색인', 'DB', '데이터베이스', 
            '디지털 아카이브', '메타데이터', '기록화', '전산화',
            '구축', '멀티미디어', '시청각', '영상'
        ],
        'RECORDS_MGMT': [
            '기록물', '정리', '기술', '이관', '인수', '평가', '폐기', 
            '실태점검', '정수점검', '공개재분류', '접근', '전수조사'
        ],
        'SPECIAL_PROJECT': [
            '컨설팅', '연구', '용역', '전략', '계획', 'ISP', '교육', 
            '훈련', '수집', '구술', '기증', '전시', '채록', '면담',
            '인터뷰', '리모델링', '개선'
        ],
        'SYSTEM_MGMT': [
            '시스템', '유지보수', '고도화', '기능개선', '보안', '백신', '인프라', 
            'HW', 'SW', '하드웨어', '소프트웨어', '라이선스', '업그레이드',
            '서버', '장비', 'virus', 'anti', '프로그램', '이전', 'S/W'
        ],
        'PRESERVATION': [
            '보존', '환경', '온습도', '공기질', '해충', '방제', '방균', '소독', 
            '서고', '보존용품', '복원', '복구', '향균', '항균', '조습', '살충',
            '모빌', '서가', '이동식', '체인', '이송', '수리'
        ]
    }

    # 프로젝트 서브타입 키워드 매핑
    PROJECT_SUBTYPE_KEYWORDS = {
        'DIGITALIZATION': {
            'PAPER_DIGITIZATION': ['종이기록물', '일반문서', '도면', '카드', '대장'],
            'SPECIAL_DIGITIZATION': ['책자', '간행물', '행정박물'],
            'AV_DIGITIZATION': ['멀티미디어', '시청각', '영상', '사진', '필름', '오디오'],
            'DIGITAL_ARCHIVE': ['아카이브', '기록화', '콘텐츠', '컨텐츠']
        },
        'RECORDS_MGMT': {
            'RECORDS_ARRANGE': ['정리', '기술', '전수조사', '목록', '분류', '메타데이터'],
            'RECORDS_TRANSFER': ['이관', '인수'],
            'RECORDS_APPRAISAL': ['평가', '폐기'],
            'RECORDS_INSPECTION': ['실태점검', '정수점검'],
            'ACCESS_CONTROL': ['공개재분류', '접근']
        },
        'SPECIAL_PROJECT': {
            'CONSULTING': ['컨설팅', '연구', '용역'],
            'PLANNING': ['전략', '계획', 'ISP', 'ISMP'],
            'EDUCATION': ['교육', '훈련'],
            'RECORDS_COLLECTION': ['수집', '구술', '기증', '채록', '면담', '인터뷰'],
            'EXHIBITION': ['전시', '상설', '기획', '순회', '콘텐츠'],
            'FACILITY_IMPROVE': ['시설', '공사', '리모델링', '개선']
        },
        'SYSTEM_MGMT': {
            'SYS_OPERATION': ['운영', '유지보수', 'HW', 'SW', '라이선스', '백업'],
            'SYS_ENHANCEMENT': ['고도화', '기능개선', '업그레이드', '이전', '설치', '전환'],
            'SECURITY_MGMT': ['보안', '백신', '문서보안', 'virus', 'anti'],
            'INFRA_ESTABLISH': ['인프라', '구축', '신규', '시스템', '장비', '서버', '교체', '노후']
        },
        'PRESERVATION': {
            'ENVIRONMENT_CONTROL': ['환경', '온습도', '공기질', '조습'],
            'PEST_PREVENTION': ['해충', '방제', '방균', '소독', '방역', '향균', '항균', '살충'],
            'STORAGE_MGMT': ['서고', '시설', '장비', '서가', '모빌', '이동식', '체인', '이송'],
            'SUPPLIES_MGMT': ['보존용품', '상자', '봉투', '용품'],
            'REPAIR_RESTORE': ['복원', '복구', '처리', '수리', '교체']
        }
    }

    # 프로젝트 타입 한글 매핑
    PROJECT_TYPE_KR = {
        'DIGITALIZATION': '전자화 사업',
        'RECORDS_MGMT': '기록물관리',
        'SPECIAL_PROJECT': '특수사업',
        'SYSTEM_MGMT': '시스템 관리',
        'PRESERVATION': '보존관리',
        'NO_PROJECT': '사업없음',
        'UNCLASSIFIED': '미분류'
    }

    # 프로젝트 서브타입 한글 매핑
    PROJECT_SUBTYPE_KR = {
        'PAPER_DIGITIZATION': '종이기록물 전자화',
        'SPECIAL_DIGITIZATION': '특수유형기록물 전자화',
        'AV_DIGITIZATION': '시청각기록물 디지털화',
        'DIGITAL_ARCHIVE': '디지털 아카이브 구축',
        'RECORDS_ARRANGE': '기록물 정리/기술',
        'RECORDS_TRANSFER': '이관/인수',
        'RECORDS_APPRAISAL': '평가/폐기',
        'RECORDS_INSPECTION': '실태점검/정수점검',
        'ACCESS_CONTROL': '공개재분류/접근관리',
        'CONSULTING': '컨설팅/연구용역',
        'PLANNING': '전략/계획수립',
        'EDUCATION': '교육/훈련',
        'RECORDS_COLLECTION': '기록물 수집',
        'EXHIBITION': '전시사업',
        'FACILITY_IMPROVE': '시설개선',
        'SYS_OPERATION': '시스템 운영/유지보수',
        'SYS_ENHANCEMENT': '시스템 고도화/개선',
        'SECURITY_MGMT': '보안관리',
        'INFRA_ESTABLISH': '인프라 구축',
        'ENVIRONMENT_CONTROL': '보존환경 관리',
        'PEST_PREVENTION': '해충방제/방균관리',
        'STORAGE_MGMT': '서고관리',
        'SUPPLIES_MGMT': '보존용품관리',
        'REPAIR_RESTORE': '복원/복구처리',
        'NO_PROJECT': '사업없음',
        'UNCLASSIFIED': '미분류'
    }

    @staticmethod
    def _find_matching_type(text, keywords_dict, check_priority=True):
        """주어진 텍스트에서 키워드 매칭을 통해 가장 적합한 타입을 찾음"""
        max_matches = 0
        best_type = None
        
        # 텍스트 전처리
        text = text.lower().strip()
        if text in ['사업없음', '미업로드', '']:
            return 'NO_PROJECT'
        
        # 우선순위 순서대로 검사 (딕셔너리 순서 유지)
        for type_name, keywords in keywords_dict.items():
            matches = sum(1 for keyword in keywords if keyword.lower() in text)
            if matches > 0:
                if check_priority:  # 프로젝트 타입 분류시에는 첫 매칭 즉시 반환
                    return type_name
                # 서브타입 분류시에는 가장 많은 매칭 선택
                if matches > max_matches:
                    max_matches = matches
                    best_type = type_name
        
        return best_type if max_matches > 0 else None

    @staticmethod
    def classify_project(project_detail: str) -> tuple:
        """
        프로젝트 상세 내용을 기반으로 프로젝트 타입과 서브타입을 분류

        Args:
            project_detail (str): 프로젝트 상세 내용

        Returns:
            tuple: (project_type_kr, project_subtype_kr)
        """
        if not project_detail or not isinstance(project_detail, str):
            return (ProjectClassifier.PROJECT_TYPE_KR['NO_PROJECT'], 
                   ProjectClassifier.PROJECT_SUBTYPE_KR['NO_PROJECT'])

        # 프로젝트 타입 분류 (우선순위 적용)
        project_type = ProjectClassifier._find_matching_type(
            project_detail, 
            ProjectClassifier.PROJECT_TYPE_KEYWORDS,
            check_priority=True
        )

        # 프로젝트 타입이 분류되지 않은 경우
        if not project_type:
            # 특수 케이스 처리
            if project_detail.lower().strip() in ['사업없음', '미업로드', '']:
                return (ProjectClassifier.PROJECT_TYPE_KR['NO_PROJECT'], 
                       ProjectClassifier.PROJECT_SUBTYPE_KR['NO_PROJECT'])
            return (ProjectClassifier.PROJECT_TYPE_KR['UNCLASSIFIED'], 
                   ProjectClassifier.PROJECT_SUBTYPE_KR['UNCLASSIFIED'])

        if project_type == 'NO_PROJECT':
            return (ProjectClassifier.PROJECT_TYPE_KR['NO_PROJECT'], 
                   ProjectClassifier.PROJECT_SUBTYPE_KR['NO_PROJECT'])

        # 해당 프로젝트 타입의 서브타입 분류
        project_subtype = ProjectClassifier._find_matching_type(
            project_detail,
            ProjectClassifier.PROJECT_SUBTYPE_KEYWORDS[project_type],
            check_priority=False
        )

        # 서브타입이 없는 경우 기본값 할당
        if not project_subtype:
            # 프로젝트 타입별 기본 서브타입 매핑
            default_subtypes = {
                'DIGITALIZATION': 'PAPER_DIGITIZATION',
                'RECORDS_MGMT': 'RECORDS_ARRANGE',
                'SPECIAL_PROJECT': 'CONSULTING',
                'SYSTEM_MGMT': 'SYS_OPERATION',
                'PRESERVATION': 'STORAGE_MGMT'
            }
            project_subtype = default_subtypes.get(project_type, 'UNCLASSIFIED')

        return (ProjectClassifier.PROJECT_TYPE_KR[project_type], 
                ProjectClassifier.PROJECT_SUBTYPE_KR[project_subtype])

    @staticmethod
    def classify_projects_in_csv(input_file: str, output_file: str = None) -> pd.DataFrame:
        """
        CSV 파일의 프로젝트들을 분류하여 새로운 컬럼 추가

        Args:
            input_file (str): 입력 CSV 파일 경로
            output_file (str, optional): 출력 CSV 파일 경로. 기본값은 None.

        Returns:
            pd.DataFrame: 분류가 추가된 데이터프레임
        """
        try:
            # CSV 파일 읽기
            df = pd.read_csv(input_file)
            
            # project_detail 컬럼이 없는 경우
            if 'project_detail' not in df.columns:
                raise ValueError("CSV 파일에 'project_detail' 컬럼이 없습니다.")

            # 프로젝트 분류 적용
            classifications = df['project_detail'].apply(ProjectClassifier.classify_project)
            df['project_type'] = [c[0] for c in classifications]
            df['project_subtype'] = [c[1] for c in classifications]

            # 결과 저장
            if output_file:
                df.to_csv(output_file, index=False, encoding='utf-8-sig')

            return df

        except Exception as e:
            print(f"오류 발생: {str(e)}")
            return None

if __name__ == "__main__":
    # 사용 예시
    import sys
    
    if len(sys.argv) < 2:
        print("사용법: python project_classifier.py input.csv [output.csv]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    result = ProjectClassifier.classify_projects_in_csv(input_file, output_file)
    
    if result is not None:
        print("분류 완료!")
        if output_file:
            print(f"결과가 {output_file}에 저장되었습니다.")
        
        # 분류 결과 통계
        print("\n사업 유형 분포:")
        print(result['project_type'].value_counts().to_string())
        
        print("\n세부 사업 유형 분포:")
        print(result['project_subtype'].value_counts().to_string()) 