import time
import threading

class Test:
    isRunning = False
    ibThread = None
    counter = 0

    def __init__(self):
        self.isRunning = True
        # self.ibThread = threading.Thread(target=self.runLoop, daemon=True)
        # self.ibThread.start()
        # time.sleep(1)

    def createContractAndRunLoop(self, symbol, strategy, id):
        self.strategyId = strategy
        print(f"Bot {id} has been created. Creating the contract...")
        print("Contract was created.")
        self.runStrategyLoop()
        print("end of runStrategyLoop")
        self.isRunning = False

    def runLoop(self):
        print("connecting..")
        while self.isRunning:
            self.counter = self.counter

    def runStrategyLoop(self):
        while self.isRunning:
            print("\n\nrunStrategyLoop cycle...")
            print("action HOLD was received. No order was placed.")
            time.sleep(3)
        self.ibThread.join()

    def stop(self):
        self.isRunning = False