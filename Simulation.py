#Hoja de trabajo 5 - Simulación DES (Discret Event Simulation)
# Alejandra Avilés - 24722; Jackelyn Girón - 24737; Sergio Tan - 24759
# Fecha de creación: 4/03/2025

import simpy, random


env = simpy.Environment()
#Semilla random para obtener los mismos resultados
seed = random.seed(21)
#Stores - son colas proporcionadas por simpy
new = simpy.Store(env)
ready = simpy.Store(env)
waiting = simpy.Store(env)

#Variables para la ram disponible, la cantidad de procesos a hacer y cuantas instrucciones se ejecutan en running
RAM_CAPACITY = 100
NUM_PROCESS = 200
EJECUTED_INSTRUCTIONS = 3

#Container para la ram - Este es un recurso compartido que puede se usado entre procesos
ram = simpy.Container(env, init=RAM_CAPACITY, capacity=RAM_CAPACITY)

#Recurso para limitar la ejecucion de procesos
cpu = simpy.Resource(env, capacity=2)


class Process:
    def __init__(self, name, ramOcupped, instructions, env):
        self.env = env
        self.name = name
        self.ramOcupped = ramOcupped
        self.instructions = instructions
        self.action = env.process(self.runEnv())

    def runEnv(self):
        #El proceso se crea y se agrega a la cola
        print(f"El proceso {self.name} llegó a la cola 'new' en el tiempo {self.env.now}")
        new.put(self)
        #Mientras no haya ram suficiente el proceso se mantendrá en la cola
        while(ram.level < self.ramOcupped):
            print(f"El proceso {self.name} está esperando en la cola en el tiempo {self.env.now}")
            yield self.env.timeout(1)
        
        #Cuando la ram sea suficiente, el proceso toma ram y se saca de la cola new y pasa a ready
        yield ram.get(self.ramOcupped)
        print(f"El proceso {self.name} tomó {self.ramOcupped} de ram en el tiempo {self.env.now}")
        pr = yield new.get()
        yield ready.put(pr)
        print(f"El proceso {self.name} se movió de 'new' a 'ready' en el tiempo {self.env.now}")

        yield env.process(self.excecuteInstructions()) #Ejecución de instrucciones

    #Función para la ejecución de instrucciones
    def excecuteInstructions(self):
        while self.instructions > 0:
            with cpu.request() as req:
                yield req #Espera hasta que el CPU este libre
                #El proceso pasa a ejecución y se le restan las instrucciones ejecutadas
                print(f"El proceso {self.name} esta ejecutandose en el tiempo {self.env.now}")
                yield self.env.timeout(1)
                self.instructions -= EJECUTED_INSTRUCTIONS
                #Si quedan instrucciones el proceso puede pasar de nuevo a la cola ready o pasa a waiting
                if self.instructions > 0:
                    option = random.choice([1,2])
                    #Pasa a waiting
                    if option == 1:
                        print(f"El proceso {self.name} esta esperando una operacion I/O en el tiempo {self.env.now}")
                        cpu.release(req)
                        yield self.env.timeout(2) #Simulación de retraso
                        waiting.put(self)
                        print(f"El proceso {self.name} paso de 'waiting' a 'ready' en el tiempo {self.env.now}")
                        yield waiting.get()
                        yield ready.put(self)
                    #Pasa directamente a ready
                    else:
                        print(f"El proceso {self.name} vuelve a la cola de ready en el tiempo {self.env.now}")
                        ready.put(self)
                #Cuando termine las instrucciones por hacer
                else:
                    yield ram.put(self.ramOcupped) #Devuelve la ram ocupada
                    print(f"El proceso {self.name} terminó y devolvió {self.ramOcupped} de ram en el tiempo {self.env.now}")


#Cración de procesos
def createProcess(env):
    for i in range(NUM_PROCESS):
        #Crear un proceso que consuma entre 1 y 10 de ram
        name = "Process" + str(i)
        ramOc = random.randint(1,10)
        process = Process(name, ramOc, ramOc,env)
        yield env.timeout(1)

#Iniciar la simulación
env.process(createProcess(env))
env.run(until=50000000000000)



