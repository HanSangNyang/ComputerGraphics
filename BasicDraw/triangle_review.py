from OpenGL.GL import * # OpenGL : 그림그리기 기초 도구
from glfw.GLFW import * # GLFW : 캔버스역할하는 window도 만들고~ 키보드 입력처리도 하고~
import glm              # glm : vec2 vec3 같은 type들 제공~ 백터 행렬 계산도 해주고~ 수학 계산 편하게 해주고~
import ctypes           # ctypes : 파이썬은 pointer가 없으니까 대신 c언어 포인터 역할 해줄 녀석~

g_vertex_shader_src = '''                   // vertex shader source를 GLSL로 선언
#version 330 core                           // OpenGL 330 버젼 사용

layout (location = 0) in vec4 vin_pos;      // 외부로부터 받은(in) vertex 의 x,y,z,w좌표(vin_pos)를 Location 0에 선언
layout (location = 1) in vec3 vin_color;    // 외부로부터 받은(in) vertex 의 색(vin_color)를 Location 1에 선언

out vec4 vout_color;                        // 선언 후 외부로 내보낼(out) vec4 타입의 color 변수 선언

void main(){
    gl_Position = vec4(vin_pos.xyz, 1.0);   // 입력받은 vertex의 좌표(in vec4 vin_pos)에 원근감을 표시하는 동차좌표(1.0)을 함께 선언함. (1.0은 기본, 0.0으로 갈수록 멀어짐)
    vout_color = vec4(vin_color,1.0);       // 입력받은 vertex의 색(in vec3 vin_color)에 투명도를 표시하는 alpha좌표(1.0)을 함께 선언함. (1.0은 불투명, 0.0은 투명)
}
'''
g_fragment_shader_src = '''                 // fragment shader source를 GLSL로 선언
#version 330 core                           // OpenGL 330 버젼 사용

in vec4 vout_color;                         // vertex shader로부터 건네받은(in) vertex의 색 정보

out vec4 FragColor;                         // 선언 후 외부로 내보낼(out) vec4 타입의 FragColor 변수 선언

void main(){
    FragColor = vout_color;                 // 입력받은(in) vertex의 색 정보를 FragColor에 선언
}
// ※주의 : vertex 각각의 색은 vertex_shader에 저장됨. fragment_shader는 rasterization이 완료되어 interpolate된 모든 픽셀들의 최종 색을 결정함.
//        본 코드의 주석에서는 편의상 vertex_shader는 위치 정보, fragment_shader는 색 정보를 담고 있다고 하겠음.
'''

def load_shaders(vertex_shader_source, fragment_shader_source): #vertex의 좌표와 색을 입력받아 shader를 생성하는 함수
    # glCreateShader(shader type{GL_VERTEX_SHADER,GL_FRAGMENT_SHADER}) : 설정한 type의 SHADER 객체를 생성하고 ID값을 반환하는 함수
    vertex_shader = glCreateShader(GL_VERTEX_SHADER)            # 생성한 SHADER 객체의 ID값으로 vertex_shader 변수를 선언

    # glShaderSource(shader_ID, GLSL source code) : ID를 받은 shader 객체의 코드를 변경함
    glShaderSource(vertex_shader, vertex_shader_source)         # vertex_shader에 vertex_shader_source(위치 정보) 입력

    # glCompileShader(shader_ID) : shader 객체를 컴파일함
    glCompileShader(vertex_shader)      # vertex_shader 컴파일

    ## shader의 comile이 성공했는지 확인
    # glGetShaderiv(shader_ID, check type) : shader의 컴파일 성공 여부를 반환
    success = glGetShaderiv(vertex_shader, GL_COMPILE_STATUS)   # shader compile의 성공 여부를 success에 입력
    if (not success):   # shader compile에 실패했을 경우
        # glGetShaderInfoLog(shader_ID) : shader compile의 실패(에러) 메시지 반환
        infoLog = glGetShaderInfoLog(vertex_shader)             # 컴파일 실패(에러) 메시지 저장
        print("ERROR:::SHADER::VERTEX:::COMPILATION_FAILED\n" + infoLog.decode())   # 컴파일 실패(에러) 메시지 출력

    fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)        # 생성한 SHADER 객체의 ID값으로 fragment_shader 변수를 선언
    glShaderSource(fragment_shader, g_fragment_shader_src)      # fragment_shader에 fragment_shader_source(색 정보) 입력
    glCompileShader(fragment_shader)                            # fragment_shader 컴파일

    success = glGetShaderiv(fragment_shader, GL_COMPILE_STATUS) # shader compile의 성공 여부를 success에 입력
    if (not success):   # shader compile에 실패했을 때
        infoLog = glGetShaderInfoLog(fragment_shader)           # 컴파일 실패(에러) 메시지 저장
        print("ERROR:::SHADER::VERTEX:::COMPILATION_FAILED\n" + infoLog.decode())   # 컴파일 실패(에러) 메시지 출력

    # glCreateProgram() : shader program 오브젝트 생성 후 ID 반환
    shader_program = glCreateProgram()              # program object 생성
    # glAttachShader(program_ID, shader) : shader program에 shader 등록
    glAttachShader(shader_program, vertex_shader)   # shader program에 vertex_shader(위치 정보) 등록
    glAttachShader(shader_program, fragment_shader) # shader program에 fragment_shader(색 정보) 등록

    # glLinkProgram(program_ID) : shader program에 등록된 shader들을 연결함
    glLinkProgram(shader_program)                   # shader program에 등록된 vertex_shader와 fragment_shader를 연결

    # glGetProgramiv(program_ID, check type), glGetProgramInfoLog(program_ID) : 각각 glGetShaderiv(), glGetShaderInfoLog()와 유사
    # glShaderiv()가 shader의 컴파일 성공을 검사했다면, glProgramiv()는 shader program의 링크를 검사함
    success = glGetProgramiv(shader_program, GL_LINK_STATUS)                    # shader program의 Linking 성공 여부 입력
    if (not success):
        infoLog = glGetProgramInfoLog(shader_program)                           # Linking 실패(에러) 메시지 저장
        print("ERROR:::SHADER::PROGRAM::LINKING_FAILED\n" + infoLog.decode())   # Linking 실패(에러) 메시지 출력

    # glDeleteShader(shader_ID) : shader 객체 제거
    glDeleteShader(vertex_shader)   # 사용이 끝난 vertex_shader 제거
    glDeleteShader(fragment_shader) # 사용이 끝난 fragment_shader 제거

    return shader_program   # parameter로 입력받은 g_vertex_shader_src, g_fragment_shader_src로 구성, 연결된 shader_program 반환

def key_callback(window, key, scancode, action, mods): # ESC키 입력 시 프로그램 종료를 위한 함수
    if key == GLFW_KEY_ESCAPE and action == GLFW_PRESS: # ESC키가(key==GLFW_KEY_ESCAPE) 눌렸을 때(action == GLFW_PRESS)
        # glfwSetWindowShouldClose(wondow, GLFW_BOOL) : GLFW_BOOL이 TRUE라면 GLFW를 종료함
        glfwSetWindowShouldClose(window, GLFW_TRUE)     # GLFW 종료

def main():
    # glfwInit() : GLFW 생성
    if not glfwInit():  # GLFW를 생성하되, 실패 시 false가 반환되어 프로그램 종료
        return
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3)  # OpenGL 3.3 (means →3 . 3)
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3)  # OpenGL 3.3 (means 3 . →3)
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE)  # Do not allow legacy OpenGl API calls

    # glfwCreateWindow(width, height, 'title', monitor, context) : window창을 생성함.
    # ps) monitor는 전체화면의 여부로, None 설정 시 창모드로 생성함. context는 window 생성 시 사용할 context로, None 설정 시 기본 context를 사용함.
    window = glfwCreateWindow(1200,1200, 'Title', None, None)
    if not window:  # window 생성에 실패했을 경우
        glfwTerminate() # glfw를 종료함
        return # 프로그램 종료

    # glfwMakeContextCurrent(window_ID) : double buffer로 사용할 window를 등록함.
    glfwMakeContextCurrent(window)  # 생성한 window를 current context에 등록
    # ※ double buffer란?
    #   window의 내용을 업데이트 할 때 생기는 깜빡임, 노이즈, 불량 픽셀의 방지를 위해 랜더링 버퍼, 디스플레잉 버퍼를 사용함
    #   랜더링 버퍼는 표시할 이미지나 그래픽을 저장하는 데 사용, 디스플레잉 버퍼는 이미지나 그래픽을 화면에 표시하는 데 사용함.
    #   랜더링이 완료된 후 glSwapBuffers(window) 함수를 이용하여 랜더링 버퍼와 디스플레잉 버퍼를 교체, 각각의 역할을 반복 수행함

    # glfwSetKeyCallback(window_ID, key_callback_function) : window에 사용할 key_callback 함수를 지정함
    glfwSetKeyCallback(window, key_callback)

    shader_program = load_shaders(g_vertex_shader_src, g_fragment_shader_src)   # 전역 변수로 선언언 v_shader소스와 f_shader소스를 이용해 shader program 생성

    # glm.array(type and size, v1, v2, ...)
    vertices = glm.array(glm.float32,
                         # position         # color
                         -0.5, -0.25, 0.0, 0.0, 0.0, 1.0, # Left vertex
                         0.5, -0.25, 0.0, 0.0, 1.0, 0.0,  # Right vertex
                         0.0, 0.8, 0.0, 1.0, 0.0, 0.0  # Top vertex
                         )  # 32bit float 타입의 값들로 vertex의 위치와 색 정보 저장 (color는 RGB값)

    # ※ Vertex Array Object(VAO) 란?
    #   사용되는 vertex들의 state들(좌표, RGB값 등)을 저장하여 반복 호출 시 CPU 자원의 낭비를 줄이는 기능

    # glGenVertexArrays(n) : n개의 vertex array 생성
    VAO = glGenVertexArrays(1)  # vertex array 1개 생성
    # glBindVertexArray(VAO_ID) : 생성된 VAO를 현재 사용할 context에 등록함
    glBindVertexArray(VAO)      # 생성한 VAO를 context에 등록

    # ※ Vertex Buffer Object(VBO) 란?
    #   OpenGL에서 그림을 그릴 때, 동일한 vertex를 여러번 사용할 때가 많음 (ex. TRIANGLE_STRIPE, TRIANGLE_FAN etc...)
    #   이에 따른 메모리의 낭비를 막기 위해 Vertex 데이터들을 저장하는 기능

    # glGenBuffers(n) : n개의 vertex buffer 생성
    VBO = glGenBuffers(1)     # vertex buffer 1개 생성
    # glBindBuffer(target, VBO_ID) : 생성된 VBO를 현재 사용할 context에 등록함
    #   target :
    #       GL_ARRAY_BUFFER : 정점(vertex) 속성 데이터 저장,
    #       GL_ELEMENT_ARRAY_BUFFER : 렌더링 인덱스(index) 속성 데이터 저장
    #       GL_UNIFORM_BUFFER : 유니폼(uniform) 속성 데이터 저장
    #       GL_TEXTURE_BUFFER : 텍스쳐(texture) 속성 데이터 저장
    glBindBuffer(GL_ARRAY_BUFFER, VBO)  # 생성한 VBO를 정점(vertex) 속성 데이터의 저장 버퍼로써 context에 등록함

    # glBufferData(target, size, data, usage) : 현재 바인드 되어있는 VBO를 위한 GPU 메모리를 할당하고, 데이터의 내용을 초기화함
    # target은 위와 동일, usage는 여러 종류가 있지만 정적 도형 그리기에 사용되는 GL_STATIC_DRAW만 알아두자
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices.ptr, GL_STATIC_DRAW)    # VBO를 위한 GPU 메모리를 vertices.nbytes 만큼 할당하고 vertices.ptr(값들)로 초기화함

    # glVertexAttribPointer(location index, size, type, normalized, stride, pointer) :  VBO에 저장된 vertex들을 어떻게 사용할 지 지정해줌
    #   location index : 전역변수로 선언했던 vin_pos 는 location = 0, vin_color 는 location = 1 이었음
    #   size : vertex의 개수
    #   type : vertex의 type
    #   normalized : 값들이 normaized된 값(ex. 1.5*10^2)인지 확인, False로 설정
    #   stride  : 속성과 속성 사이의 간격
    #   pointer : 버퍼에서 첫 정점 속성의 위치(offset)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * glm.sizeof(glm.float32), None)
    #   0 : vin_pos의 location = 0
    #   3 : 각 vertex가 3개씩 위치값(x, y, z)을 가짐
    #   GL_FLOAT : vertex의 위치값 type
    #   GL_FALSE : normalized 되어있지 않음
    #   6 * glm.sizeof(glm.float32) : 값 당 float32 크기를 갖고, vertex의 첫 값부터 다음 번째 vertex의 첫 값까지 6개 값 만큼의 stride를 가짐
    #   None : vin_pos 값은 0번부터 시작함

    # glEnableVertexAttribArray(n) : n번 location의 vertex attribute를 활성화함
    glEnableVertexAttribArray(0)    # location 0번 활성화

    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * glm.sizeof(glm.float32), ctypes.c_void_p(3 * glm.sizeof(glm.float32)))
    #   1 : vin_color의 location = 1
    #   3 : 각 vertex가 3개씩 색 값(R, G, B)을 가짐
    #   GL_FLOAT : vertex의 색 값 type
    #   GL_FALSE : normalized 되어있지 않음
    #   6 * glm.sizeof(glm.float32) : 값 당 float32 크기를 갖고, vertex의 첫 값부터 다음 번째 vertex의 첫 값까지 6개 값 만큼의 stride를 가짐
    #   ctypes.c_void_p(3 * glm.sizeof(glm.float32) : vin_color 값은 첫번째 vertex의 vin_pos값들이 끝난 지점)부터 시작함
    glEnableVertexAttribArray(1)    # location 1번 활성화

    while not glfwWindowShouldClose(window): # glfw가 종료 명령을 받을 때 까지 루프
        # glClear(buffer_type) : 파라미터에 해당하는 버퍼를 지움
        #   glClear(GL_COLOR_BUFFER_BIT) : 색상 버퍼를 지움
        #   ※지운다고 표현했지만, glClearColor(R,G,B,A)로 설정한 색으로 배경을 '덮는다'는 느낌이다. (설정 안했을 시 검정색으로 덮음)
        glClear(GL_COLOR_BUFFER_BIT) # window의 배경색 초기화

        # glUseProgram(program_ID) : shader program 활성화
        glUseProgram(shader_program)    # shader_program 활성화

        # glDrawArrays(rendering type, first, count) : rendering type에 맞게 first 인덱스부터 총 count 개수 만큼의 인덱스를 rendering함
        glDrawArrays(GL_TRIANGLES, 0, 3)    # GL_TRIANGLES : vertex 3개씩 삼각형의 꼭짓점을 구성함, 0 : 0번째 인덱스 vertex부터, 3 : 총 3개의 vertex 사용

        # glfwSwapBuffers(window) : double buffer(렌더링 버퍼와 디스플레잉 버퍼)를 스왑함
        glfwSwapBuffers(window) # double buffer 스왑

        # glfwPollEvents() : 보류 중인 모든 키 이벤트 검색 및 수행
        glfwPollEvents()    # 루프마다 key_callback을 호출하여 키 입력 활성화

    glfwTerminate() # 루프 종료 후 glfw 종료

# if __name__ == "__main__"
# 파이썬은 어떤 모듈이든 main으로 실행될 수 있다.
# 이때 main 모듈에서 타 모듈을 실행 시, 해당 모듈에서 __name__ 변수는 그 모듈의 이름을 반환한다.
# 하지만 main 모듈에서 __name__은 main 모듈의 이름이 아닌 __main__ 을 반환한다.
# 즉, 위와 같은 if 문을 사용하면 해당 모듈이 main으로 실행되었을때만 이후 코드를 수행하게 된다.
if __name__ == "__main__" : # 본 파일이 main으로 실행되었을 때,
    main()  # main() 실행
