"""Optional orderly end-of-verification cleanup, never a crash exit bypass.

The original245 crash is not yet reproduced by the minimal or Qt runtime
subset. This routine's actual object destruction is verified independently;
apply only with full-range diagnostics and retain the true process exit code.
"""


def shutdown_verification_qt(wait_milliseconds=5000):
    """After all checks, drain Qt workers and destroy remaining Qt objects."""
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import QCoreApplication, QEvent, QThreadPool
    import shiboken6
    app = QApplication.instance()
    if app is None:
        return {'application_present': False, 'application_destroyed': True,
                'top_level_widgets_before_shutdown': 0, 'valid_wrappers_after_shutdown': 0}
    pool = QThreadPool.globalInstance()
    active = pool.activeThreadCount()
    # Wait before destroying receivers. Failure propagates to the verifier.
    if not pool.waitForDone(wait_milliseconds):
        raise RuntimeError('Qt verification workers did not finish before shutdown.')
    app.processEvents()
    widgets = list(app.topLevelWidgets())
    for widget in widgets:
        widget.close()
        widget.deleteLater()
    app.processEvents()
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    app.shutdown()
    alive = sum(shiboken6.isValid(widget) for widget in widgets)
    destroyed = QApplication.instance() is None
    if not destroyed or alive:
        raise RuntimeError('Qt verification application/widgets survived explicit shutdown.')
    return {'application_present': True, 'active_pool_threads_before_wait': active,
            'application_destroyed': destroyed, 'top_level_widgets_before_shutdown': len(widgets),
            'valid_wrappers_after_shutdown': alive}
