# labeling_tool
!!!!!!!!!!!!!등록 작업시 디바이스의 123.123.123.123/2는 삭제하지 말아주시기 바랍니다!!!!!!!!!!!!!
    
  임시로 공유한 툴이기 때문에 메뉴얼도 미흡하고 미완성된 부분이 많습니다. 주석 후 수정된 코드도 많고 주석을 달지못한 코드도 있습니다. 사용, 확인해보시고 수정해야할 점 Github이나 Notion에 최대한 많이 올려주시기 바랍니다~   
    
## 필요 설치모듈  
Python3.7, PyQt5(5.14), opencv-python(4.2.0.34), pillow(7.1.2), paho-mqtt(1.5.0), PyMySQL(0.9.3) 추후 한번에 설치할 수 있는 스크립트를 추가할 예정입니다
  
## 참고사항  
main.py를 실행시킨 후 등록 -> 촬영 -> 검수 -> 라벨링 -> 합성 순으로 작업을 진행  
  
<img src="https://user-images.githubusercontent.com/46614789/84610354-3f461700-aef5-11ea-8228-91c0946c4626.png"  width="30%" height="30%">
  
main.py를 실행시켰을 때 생성되는 창 -> 최상위 화면  
  
각 단계의 버튼을 클릭하면 해당 작업을 수행할 수 있는 새로운 창이 생성  
  
DB에 관련된 버튼(파란버튼)을 DB와 연동되는 작업은 없기 때문에 기능적으로 잘못 된 작업을 돌릴 수 없거나 렉이 걸릴 경우 창을 재시작해도 무관  
  
DB의 데이터를 기준으로 모든 GUI가 구성되어 있기 때문에 작업 완료 후 특별한 액션을 취하지 않고 창을 닫은 후 다음 작업을 진행  
  
파란색 버튼들은 클릭할 경우 DB에 접근하는 버튼이기 때문에 비정상적인 상황에서 클릭하면 프로그램이 죽거나 데이터가 잘못 저장될 수 있음  
  
나머지 버튼 및 작업들은 로컬 변수로만 동작하는 버튼  
(**검수작업의 허락, 거절 버튼은 DB와 연동되어 있지만 그 기능 상, 다른색으로 지정**)  
  
작업 순서에따라 작업하지 않고 DB를 직접 건드려서 작업하는 경우 툴을 사용할 수 없는 경우가 있으니 왠만하면 툴에서 모든 작업 진행  
  
erase.py를 실행시킬 경우 DB에 존재하는 모든 데이터를 삭제할 수 있음. 현재는 작업공간이 공유되어 있기 때문에 DB를 날릴 경우 단톡방에 다른 작업이 진행중인지 물어본 후 삭제 요망  
  
  
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
    이름 : (str)**(언더바("_"), 슬래시("/"), 띄어쓰기(" ")는 들어갈 경우 뒤의 코드에서 에러 발생)**  
    가로 : 1\~x (정수)  
    깊이 : 1\~x (정수)  
    높이 : 1\~x (정수)  
    촬영 횟수 : 1\~x (정수)  
    이미지 : 찾기 버튼 클릭 후 파일 선택  
    
  <img src="https://user-images.githubusercontent.com/46614789/85643538-6fe53800-b6cf-11ea-976c-2412416c3d25.png"  width="60%" height="30%">  
  
### 촬영
---
Environment, Category, Grid를 선택하여 촬영하고 싶은 물품을 선택 하고 촬영하는 환경  
1. 원하는 디바이스, 그리드 선택  
  <img src="https://user-images.githubusercontent.com/46614789/86326580-e5777800-bc7c-11ea-95f6-77ce4f08f65f.png"  width="60%" height="30%">  
2. 물품 리스트에서 원하는 물품을 선택 후, ->버튼 클릭(추가할 물품 리스트로 물품 이동)  
  <img src="https://user-images.githubusercontent.com/46614789/86326590-e90aff00-bc7c-11ea-88d0-5c778a58c5fe.png"  width="60%" height="30%">  
3. 원하는 물품을 모두 추가할 물품 리스트로 옮긴 후, 물건추가 버튼 클릭  
  <img src="https://user-images.githubusercontent.com/46614789/86326597-ea3c2c00-bc7c-11ea-8a31-c547be6d1421.png"  width="60%" height="30%">  
4. 원하는 그리드, 물품조합을 모두 추가할 때 까지 2,3 과정 반복  
  <img src="https://user-images.githubusercontent.com/46614789/86326601-eb6d5900-bc7c-11ea-9eef-5b9a8618b22c.png"  width="60%" height="30%">  
  우측 공간에 물품을 잘못 추가했을 경우, 해당 항목을 클릭한 후, 삭제(Delete)버튼을 누르면 해당 항목이 제거됨
5. 확인버튼 클릭  
  <img src="https://user-images.githubusercontent.com/46614789/84611140-e6c44900-aef7-11ea-976a-adf1e6462c2d.png"  width="60%" height="30%">  
6. 촬영  
  촬영버튼을 누르면 냉장고 문이 열리고 물품을 배치 후, 문을 닫으면 사진이 찍힘  
  
  
### 검수
---
촬영된 이미지가 데이터로 쓰일 수 있는지 체크하는 환경   
1. 원하는 카테고리와 그리드 선택  
  <img src="https://user-images.githubusercontent.com/46614789/84611733-a6fe6100-aef9-11ea-8159-cf839288ca7c.png"  width="60%" height="30%">  
2. 허락(거절)할 오브젝트들 선택  
  <img src="https://user-images.githubusercontent.com/46614789/84611737-a8c82480-aef9-11ea-928f-c631ad98e11d.png"  width="60%" height="30%">  
3. 허락(거절)버튼 클릭  
  <img src="https://user-images.githubusercontent.com/46614789/84611739-a960bb00-aef9-11ea-932b-ac1a23967355.png"  width="60%" height="30%">  
4. 허락(거절)된 버튼을 제외한 나머지 버튼 클릭 및 거절  
  <img src="https://user-images.githubusercontent.com/46614789/84611740-a9f95180-aef9-11ea-8d26-b3eb38c107e2.png"  width="60%" height="30%">  
  
  한번 허락하거나 거절해서 버튼색이 변한 버튼도 다시 거절, 허락 할 수 있음. 단, 한번 리스트를 갱신하거나 창을 재시작하면 허락된 오브젝트들은 나타나지 않음
**(허락한 데이터는 추후 검수리스트에 보이지 않으니 신중히 선택)** 
  
### 라벨링
---
검수된 이미지에 비박스와 마스크를 그리는 환경  
  <img src="https://user-images.githubusercontent.com/46614789/84733391-126b3000-afd9-11ea-887c-a4a11a8268cc.png"  width="60%" height="30%">  
  
1. 좌측 상단에서 원하는 물품을 선택  
2. 원하는 오브젝트 선택 후 작업   
3. **작업 후 저장 버튼 클릭**  
4. 라벨링을 실수했을 경우 다시 그리면 자동으로 기존의 라벨은 사라짐
5. 약간의 수정만 하면 될 경우, 우측 상단의 수정 버튼을 눌러 수정 환경으로 바꾼 후 수정  
6. 수정후 **저장**  
  
※작업 진행도는 체크박스를 기준으로 카운트됨 저장을 누를 경우 체크박스가 채워지며, 임의로 해제도 가능  
※마스크, 비박스는 한 오브젝트에 하나만 존재하므로 이미 비박스, 마스크가 존재하는 상황에서 마스크, 비박스를 그릴 경우 기존의 것을 사라지고 새로 그려짐
  
**단축키**  
  수정 환경으로 전환 - E  
  화면에 가득차는 기본 사이즈로 변환 - G  
  다음 이미지 - D  
  이전 이미지 - A  
  박스(마스크) 작업 환경으로 전환 - Q    
  저장 - S  
  확대 - Ctrl + 스크롤  
  화면이동 - Ctrl + 좌클릭드래그  
      
  단축키는 해당 버튼위에 마우스를 올리면 툴팁으로 표시 됨  
    
##### 비박스  
클릭 후 드래그하여 작업  
  
##### 마스크  
좌클릭으로 포인트를 정한 후, 최종 우클릭을 하면 마지막 포인트와 첫 포인트가 이어짐  
  
### Mix 비박싱  
---
Mix 데이터는 테스트 데이터로 합성하기 위해 사용되는 마스크 작업을 할 필요가 없음
  
작업방식은 기존 라벨링과 동일하나 박스가 여러개 존재할 수 있으며, 특정 박스를 선택하여 삭제, 라벨수정을 할 수 있음
  
삭제 : 수정 환경에서 원하는 마스크 내부를 클릭한 뒤 삭제버튼 클릭
  
라벨수정 : 변경하고 싶은 라벨과 마스크를 선택한 뒤 라벨수정 버튼 클릭  
  
  <img src="https://user-images.githubusercontent.com/46614789/86441947-ede8b500-bd47-11ea-88d0-6e22d6e41da2.png"  width="60%" height="30%">  
  
  수정 태에서 마스크를 클릭할 경우 좌측 상단에 물품정보가 표시되며, 해당마스크를 삭제, 현재 우측에서 선택되어있는 라벨로 라벨수정이 가능함  
  
  <img src="https://user-images.githubusercontent.com/46614789/86441950-efb27880-bd47-11ea-80a4-467a5ba89487.png"  width="60%" height="30%">  
    
  다음 라벨을 클릭할 경우 현재 작업라벨(우측에 선택되어 있는 라벨)이 다음 라벨로 바뀜  
    
  이전 라벨을 클릭할 경우 현재 작업라벨(우측에 선택되어 있는 라벨)이 이전 라벨로 바뀜  
  
### 합성
---
라벨링된 데이터를 합성하여 학습 데이터를 생성하는 환경  
  
합성 환경을 설정하기위해 그리드, 배경, 물품을 선택  
(물품별 그리드 기능과 augment 옵션 기능은 현재 합성에선 사용되지 않는다)  

<img src="https://user-images.githubusercontent.com/46614789/86327272-f5438c00-bc7d-11ea-8be7-52509aec3664.png"  width="60%" height="30%">  
  
합성하기 클릭  
  
  

### 지그오픈
---
지그를 열고 닫을 때 사진을 찍어 띄워주는 버튼(해당기능은 라벨링 작업과 무관)

