# labeling_tool
## 참고사항
Practice.py를 실행시킨 후 등록 -> 촬영 -> 검수 -> 라벨링 -> 합성 순으로 작업을 진행  
  
<img src="https://user-images.githubusercontent.com/46614789/84610354-3f461700-aef5-11ea-8228-91c0946c4626.png"  width="30%" height="30%">
  
Practice.py를 실행시켰을 때 생성되는 창 -> 최상위 화면  
  
각 단계의 버튼을 클릭하면 해당 작업을 수행할 수 있는 새로운 창이 생성  
  
DB에 관련된 버튼(파란버튼)을 DB와 연동되는 작업은 없기 때문에 기능적으로 잘못 된 작업을 돌릴 수 없거나 렉이 걸릴 경우 창을 재시작해도 무관  
  
DB의 데이터를 기준으로 모든 GUI가 구성되어 있기 때문에 작업 완료 후 특별한 액션을 취하지 않고 창을 닫은 후 다음 작업을 진행  
  
파란색 버튼들은 클릭할 경우 DB에 접근하는 버튼이기 때문에 비정상적인 상황에서 클릭하면 프로그램이 죽거나 데이터가 잘못 저장될 수 있음  
  
나머지 버튼 및 작업들은 로컬 변수로만 동작하는 버튼  
(**검수작업의 허락, 거절 버튼은 DB와 연동되어 있지만 그 기능 상, 다른색으로 지정**)  
  
### 등록
---
Environment, Grid, SuperCategory, Category 정보를 등록하는 작업 환경   
**등록 작업에서 데이터를 등록할 경우 반드시 아래의 형식대로 등록** 
  
디바이스  
    IP : xxx.xxx.xxx.xxx  (x는 0\~9 정수)  
    층수 : 1\~x (정수)  
    가로 : 1\~x (정수)  
    깊이 : 1\~x (정수)  
    높이 : 1\~x (정수)  
  
그리드  
    x : 1\~x(정수)  
    y : 1\~x(정수)  
    예외 : mix전용 그리드는 x = 0, y = 0 으로 입력  
  
분류  
    분류 : (str)(mix전용 분류 : mix, background전용 분류 : background)  
  
물품등록  
    분류 : 이름 위의 박스에서 물품의 분류를 선택(mix물품은 반드시 분류 : mix를, 물품 background는 반드시 분류 : background를 선택)  
    이름 : (str)(언더바("_"), 슬래시("/"), 띄어쓰기(" ")는 들어갈 경우 뒤의 코드에서 에러 발생)  
    가로 : 1\~x (정수)  
    깊이 : 1\~x (정수)  
    높이 : 1\~x (정수)  
    촬영 횟수 : 1\~x (정수)  
    이미지 : 찾기 버튼 클릭 후 파일 선택  
    
  <img src="https://user-images.githubusercontent.com/46614789/84611142-e75cdf80-aef7-11ea-8451-4580c4123602.png"  width="30%" height="30%">  
  
### 촬영
---
Environment, Category, Grid를 선택하여 촬영하고 싶은 물품을 선택 하고 촬영하는 환경  
1. 원하는 디바이스, 그리드 선택  
  <img src="https://user-images.githubusercontent.com/46614789/84611133-e461ef00-aef7-11ea-8636-15c946cc3e35.png"  width="30%" height="30%">  
2. 물품 리스트에서 원하는 물품을 선택 후, ->버튼 클릭(추가할 물품 리스트로 물품 이동)  
  <img src="https://user-images.githubusercontent.com/46614789/84611135-e5931c00-aef7-11ea-84d8-ea3699689f57.png"  width="30%" height="30%">  
3. 원하는 물품을 모두 추가할 물품 리스트로 옮긴 후, 물건추가 버튼 클릭  
  <img src="https://user-images.githubusercontent.com/46614789/84611137-e5931c00-aef7-11ea-926b-3fdb3bdbe2eb.png"  width="30%" height="30%">  
4. 원하는 그리드, 물품조합을 모두 추가할 때 까지 2,3 과정 반복  
  <img src="https://user-images.githubusercontent.com/46614789/84611138-e62bb280-aef7-11ea-8e66-f89b927c6ce1.png"  width="30%" height="30%">  
5. 확인버튼 클릭  
  <img src="https://user-images.githubusercontent.com/46614789/84611140-e6c44900-aef7-11ea-976a-adf1e6462c2d.png"  width="30%" height="30%">  
6. 촬영  
  
  
### 검수
---
촬영된 이미지가 데이터로 쓰일 수 있는지 체크하는 환경   
1. 원하는 카테고리와 그리드 선택  
  <img src="https://user-images.githubusercontent.com/46614789/84611733-a6fe6100-aef9-11ea-8159-cf839288ca7c.png"  width="30%" height="30%">  
2. 허락(거절)할 오브젝트들 선택  
  <img src="https://user-images.githubusercontent.com/46614789/84611737-a8c82480-aef9-11ea-928f-c631ad98e11d.png"  width="30%" height="30%">  
3. 허락(거절)버튼 클릭  
  <img src="https://user-images.githubusercontent.com/46614789/84611739-a960bb00-aef9-11ea-932b-ac1a23967355.png"  width="30%" height="30%">  
4. 허락(거절)된 버튼을 제외한 나머지 버튼 클릭 및 거절  
  <img src="https://user-images.githubusercontent.com/46614789/84611740-a9f95180-aef9-11ea-8d26-b3eb38c107e2.png"  width="30%" height="30%">  
  
  한번 허락하거나 거절해서 버튼색이 변한 버튼도 다시 거절, 허락 할 수 있음. 단, 한번 리스트를 갱신하거나 창을 재시작하면 허락된 오브젝트들은 나타나지 않음
**(허락한 데이터는 추후 검수리스트에 보이지 않으니 신중히 선택)** 
  
라벨링  
검수된 이미지에 비박스와 마스크를 그리는 환경  

합성  
라벨링된 데이터를 합성하여 학습 데이터를 생성하는 환경  

지그오픈  
지그를 열고 닫을 때 사진을 찍어 띄워주는 버튼   

