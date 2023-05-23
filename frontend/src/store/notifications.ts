import { DEFAULT_TOAST_DURATION } from '@/constants'
import { Subject } from 'rxjs'

export interface IToast {
  message: string
  duration?: number
  position?: 'center' | 'left'
  isInfinite?: boolean
  type?: 'success' | 'error' | 'info' | 'default'
  // isPersistent?: boolean // Currently has no effect
}

export interface IDialog {
  title: string
  content: string
  confirmText?: string
  secondaryActionText?: string
  cancelText?: string
  onConfirm: () => any
  onSecondaryAction?: () => any
  onCancel?: () => any
}

export default class Notification {
  static entity = 'notification'
  static toast$ = new Subject<IToast>()
  static dialog$ = new Subject<IDialog>()

  static toast(params: IToast) {
    this.toast$.next({
      ...params,
      duration:
        params.duration !== undefined
          ? params.duration
          : DEFAULT_TOAST_DURATION,
      position: params.position || 'center',
      isInfinite: !!params.isInfinite,
      type: params.type,
      // isPersistent: params.isPersistent !== undefined ? params.isPersistent : true,
    })
  }

  static openDialog(params: IDialog) {
    this.dialog$.next(params)
  }
}
