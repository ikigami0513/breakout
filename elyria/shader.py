from OpenGL.GL import *
import glm


class Shader:
    def __init__(self, vertex_path: str, fragment_path: str, geometry_path: str = None) -> None:
        # 1. retrieve the vertex/fragment source code from filepath
        try:
            # open files
            v_shader_file = open(vertex_path)
            f_shader_file = open(fragment_path)

            # read file's buffer contents into strings
            vertex_code = v_shader_file.read()
            fragment_code = f_shader_file.read()

            # close file handlers
            v_shader_file.close()
            f_shader_file.close()

            geometry_code = None

            if geometry_path:
                g_shader_file = open(geometry_path)
                geometry_code = g_shader_file.read()
                g_shader_file.close()

            # 2. compile shaders
            # vertex shader
            vertex = glCreateShader(GL_VERTEX_SHADER)
            glShaderSource(vertex, vertex_code)
            glCompileShader(vertex)
            self.check_compile_errors(vertex, "VERTEX")

            # fragment shader
            fragment = glCreateShader(GL_FRAGMENT_SHADER)
            glShaderSource(fragment, fragment_code)
            glCompileShader(fragment)
            self.check_compile_errors(fragment, "FRAGMENT")

            # geometry shader
            if geometry_path:
                geometry = glCreateShader(GL_GEOMETRY_SHADER)
                glShaderSource(geometry, geometry_code)
                glCompileShader(geometry)
                self.check_compile_errors(geometry, "GEOMETRY")

            # shader program
            self.id = glCreateProgram()
            glAttachShader(self.id, vertex)
            glAttachShader(self.id, fragment)

            if geometry_path:
                glAttachShader(self.id, geometry)

            glLinkProgram(self.id)
            self.check_compile_errors(self.id, "PROGRAM")

            # delete the shaders as they're linked into our program now and no longer necessary
            glDeleteShader(vertex)
            glDeleteShader(fragment)
            if geometry_path:
                glDeleteShader(geometry)

        except IOError:
            print("ERROR::SHADER::FILE_NOT_SUCCESSFULLY_READ")

    def use(self) -> None:
        # activate the shader
        glUseProgram(self.id)

    # utility uniform function
    def set_bool(self, name: str, value: bool) -> None:
        glUniform1i(glGetUniformLocation(self.id, name), int(value))

    def set_int(self, name: str, value: int) -> None:
        glUniform1i(glGetUniformLocation(self.id, name), value)

    def set_float(self, name: str, value: float) -> None:
        glUniform1f(glGetUniformLocation(self.id, name), value)

    def set_vec2(self, name: str, *args) -> None:
        if len(args) == 1 and type(args[0]) == glm.vec2:
            glUniform2fv(glGetUniformLocation(self.id, name), 1, glm.value_ptr(args[0]))
        elif len(args) == 2 and all(map(lambda x: type(x) == float, args)):
            glUniform2f(glGetUniformLocation(self.id, name), *args)

    def set_vec3(self, name: str, *args) -> None:
        if len(args) == 1 and type(args[0]) == glm.vec3:
            glUniform3fv(glGetUniformLocation(self.id, name), 1, glm.value_ptr(args[0]))
        elif len(args) == 3 and all(map(lambda x: type(x) == float, args)):
            glUniform3f(glGetUniformLocation(self.id, name), *args)

    def set_vec4(self, name: str, *args) -> None:
        if len(args) == 1 and type(args[0]) == glm.vec4:
            glUniform4fv(glGetUniformLocation(self.id, name), 1, glm.value_ptr(args[0]))
        elif len(args) == 4 and all(map(lambda x: type(x) == float, args)):
            glUniform4f(glGetUniformLocation(self.id, name), *args)

    def set_mat2(self, name: str, mat: glm.mat2) -> None:
        glUniformMatrix2fv(glGetUniformLocation(self.id, name), 1, GL_FALSE, glm.value_ptr(mat))

    def set_mat3(self, name: str, mat: glm.mat3) -> None:
        glUniformMatrix3fv(glGetUniformLocation(self.id, name), 1, GL_FALSE, glm.value_ptr(mat))

    def set_mat4(self, name: str, mat: glm.mat4) -> None:
        glUniformMatrix4fv(glGetUniformLocation(self.id, name), 1, GL_FALSE, glm.value_ptr(mat))

    def check_compile_errors(self, shader: int, type: str) -> None:
        if type != "PROGRAM":
            success = glGetShaderiv(shader, GL_COMPILE_STATUS)
            if not success:
                info_log = glGetShaderInfoLog(shader)
                print(f"ERROR::SHADER_COMPILATION_ERROR of type {type}\n{info_log.decode()}")
        else:
            success = glGetProgramiv(shader, GL_LINK_STATUS)
            if not success:
                info_log = glGetProgramInfoLog(shader)
                print(f"ERROR::PROGRAM_LINKING_ERROR of type {type}\n{info_log.decode()}")
