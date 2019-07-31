'''Matlab Util
@author: Li Shu
@date: 2019/6/6
'''
import matlab
import matlab.engine as megn
import io

def matlab_output_to_python(out,err):
    """
    将matlab命令行里的输出内容转移到python会话中便于分析。
    """  
    if  err.getvalue() != '':
        print('err message: ', err.getvalue())
    if  out.getvalue() != '':
        print('out message: ', out.getvalue())
    out.close() # 在函数体内关闭out和err，主函数中也会关闭。
    err.close()
    return io.StringIO(), io.StringIO() # 在函数体生成新的out,err并返回到主函数中。       

def new_matlab_engine(matlab_mode):
    """
    matlab_mode = 0 ，创建一个新的matlab会话。
    matlab_mode = 1 ，连接到一个已经打开的matlab共享会话（窗口）。
    连接到共享 MATLAB 会话的过程: 
    首先，从 MATLAB 调用 matlab.engine.shareEngine 将其转换为共享会话。
    若没有这句话，则megn.find_matlab() 不会找到该matlab会话。
    matlab_mode 为其他，返回None。
    """  
    if matlab_mode == 0:
        return megn.start_matlab() 
    elif matlab_mode == 1:
        matlab_number = megn.find_matlab()[0]
        return megn.connect_matlab(matlab_number,async=False)
    else:
        return None



