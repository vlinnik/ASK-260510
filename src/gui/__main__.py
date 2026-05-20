from importlib import resources 

def workdir():  #pysca использует механизм entry-points для запуска проекта, надо только знать где data
    return resources.files("gui").joinpath("data")

#запуск проекта cli-утилитой pysca.cli
def main():
    from pysca.cli.project import app
    app()
    
if __name__=="__main__":
    main()