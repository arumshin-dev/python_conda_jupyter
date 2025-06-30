# closure example - decorator
# 클로저(closure) 예제 - 데코레이터처럼 동작할 수 있음

# HTML 태그를 만들어주는 함수
def tag_func(tag, text):
  # 외부 함수의 매개변수들을 내부 함수에서 사용할 수 있게 클로저로 구성
  text = text  # 이 라인은 실제로 없어도 무방 (그대로 할당이라 의미 없음)
  tag = tag    # 위와 동일

  # 내부 함수 정의 (클로저)
  def inner_func():
    # 문자열 포맷팅을 이용해 HTML 태그 형태로 문자열을 반환
    # return f"<{tag}>{text}</{tag}>"  # f-string 버전
    return "<{0}>{1}</{0}>".format(tag, text)  # format 메서드 버전

  return inner_func  # 내부 함수 자체를 반환 (실행 X)

# h1 태그용 클로저 생성
h1_func = tag_func("h1", "Hello World")
# p 태그용 클로저 생성
p_func = tag_func("p", "Hello World")

# 클로저 실행: 각각의 태그가 적용된 문자열 반환
print(h1_func())  # <h1>Hello World</h1>
print(p_func())   # <p>Hello World</p>
