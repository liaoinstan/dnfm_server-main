class EventManager:
    def __init__(self):
        self.subscribers = {}

    def subscribe(self, event_name, callback):
        if event_name not in self.subscribers:
            self.subscribers[event_name] = []
        self.subscribers[event_name].append(callback)

    def publish(self, event_name, *args, **kwargs):
        if event_name in self.subscribers:
            for callback in self.subscribers[event_name]:
                callback(*args, **kwargs)

# 创建事件管理器实例
eventManager = EventManager()

# # 定义订阅者函数
# def subscriber_function(message):
#     print("Received message:", message)

# # 订阅事件
# event_manager.subscribe('example_event', subscriber_function)

# # 发布事件
# event_manager.publish('example_event', 'Hello, EventManager!')
