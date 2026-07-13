"""异步任务管理器 - 避免UI冻结"""

import traceback
from PySide6.QtCore import QObject, Signal, QThread, QRunnable, QThreadPool, Slot


class WorkerSignals(QObject):
    """工作线程信号"""
    finished = Signal()  # 完成信号
    error = Signal(str)  # 错误信号
    result = Signal(object)  # 结果信号
    progress = Signal(str)  # 进度信号


class AnalysisWorker(QRunnable):
    """分析任务工作线程"""
    
    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        self.setAutoDelete(True)
    
    @Slot()
    def run(self):
        """执行任务"""
        try:
            self.signals.progress.emit("开始分析...")
            result = self.func(*self.args, **self.kwargs)
            self.signals.result.emit(result)
        except Exception as e:
            error_msg = f"{str(e)}\n{traceback.format_exc()}"
            self.signals.error.emit(error_msg)
        finally:
            self.signals.finished.emit()


class TaskManager(QObject):
    """任务管理器"""
    
    task_started = Signal(str)  # 任务开始信号
    task_finished = Signal(str, object)  # 任务完成信号
    task_error = Signal(str, str)  # 任务错误信号
    task_progress = Signal(str, str)  # 任务进度信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._pool = QThreadPool.globalInstance()
        self._active_tasks = {}
    
    def submit_task(self, task_id: str, func, *args, **kwargs):
        """提交异步任务"""
        worker = AnalysisWorker(func, *args, **kwargs)
        
        # 连接信号
        worker.signals.finished.connect(lambda: self._on_task_finished(task_id))
        worker.signals.result.connect(lambda result: self._on_task_result(task_id, result))
        worker.signals.error.connect(lambda error: self._on_task_error(task_id, error))
        worker.signals.progress.connect(lambda msg: self.task_progress.emit(task_id, msg))
        
        self._active_tasks[task_id] = worker
        self.task_started.emit(task_id)
        
        # 提交到线程池
        self._pool.start(worker)
    
    def _on_task_finished(self, task_id: str):
        """任务完成"""
        if task_id in self._active_tasks:
            del self._active_tasks[task_id]
    
    def _on_task_result(self, task_id: str, result):
        """任务结果"""
        self.task_finished.emit(task_id, result)
    
    def _on_task_error(self, task_id: str, error: str):
        """任务错误"""
        self.task_error.emit(task_id, error)
    
    def cancel_all(self):
        """取消所有任务"""
        self._pool.clear()
        self._active_tasks.clear()


# 全局任务管理器实例
_task_manager = None


def get_task_manager() -> TaskManager:
    """获取全局任务管理器"""
    global _task_manager
    if _task_manager is None:
        _task_manager = TaskManager()
    return _task_manager
