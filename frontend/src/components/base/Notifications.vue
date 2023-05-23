<template>
  <v-dialog v-model="dialog.isActive" width="60rem">
    <v-card>
      <v-card-title>{{ dialog.title }}</v-card-title>
      <v-card-text>
        {{ dialog.content }}
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn @click="cancel()">{{ dialog.cancelText }}</v-btn>
        <v-btn v-if="dialog.onSecondaryAction" @click="secondaryAction()">{{
          dialog.secondaryActionText
        }}</v-btn>
        <v-btn @click="confirm()" color="primary">{{
          dialog.confirmText
        }}</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <v-snackbar
    v-model="snackbar.isActive"
    :timeout="snackbar.isInfinite ? -1 : snackbar.duration"
    multi-line
  >
    {{ snackbar.message }}

    <template v-slot:actions>
      <v-btn color="red" variant="text" @click="snackbar.isActive = false">
        Dismiss
      </v-btn>
    </template>
  </v-snackbar>
</template>

<script lang="ts" setup>
import { DEFAULT_TOAST_DURATION } from '@/constants'
import { Subscription } from 'rxjs'
import { reactive, onBeforeUnmount } from 'vue'
import Notification, { IDialog, IToast } from '@/store/notifications'

const INITIAL_DIALOG = {
  title: '',
  content: '',
  confirmText: 'Accept',
  cancelText: 'Cancel',
  isActive: false,
  onConfirm: () => {},
  onCancel: () => {},
}

const INITIAL_SNACKBAR = {
  message: '',
  duration: DEFAULT_TOAST_DURATION,
  position: 'center' as 'center' | 'left' | undefined,
  type: 'default' as 'default' | 'success' | 'error' | 'info',
  isActive: false,
  isInfinite: false,
  // isPersistent: false,
}

const snackbar: IToast & { isActive: boolean; isInfinite: boolean } =
  reactive(INITIAL_SNACKBAR)
const dialog: IDialog & { isActive: boolean } = reactive(INITIAL_DIALOG)

const onToast: Subscription = Notification.toast$.subscribe(
  (nextToast: IToast) => {
    snackbar.message = nextToast.message
    snackbar.isInfinite = nextToast.isInfinite || INITIAL_SNACKBAR.isInfinite
    snackbar.position = nextToast.position || INITIAL_SNACKBAR.position
    snackbar.type = nextToast.type || INITIAL_SNACKBAR.type
    snackbar.isActive = true
  }
)

const onOpenDialog: Subscription = Notification.dialog$.subscribe(
  (nextDialog: IDialog) => {
    dialog.cancelText = nextDialog.cancelText
    dialog.confirmText = nextDialog.confirmText
    dialog.content = nextDialog.content
    dialog.onCancel = nextDialog.onCancel
    dialog.onConfirm = nextDialog.onConfirm
    dialog.onSecondaryAction = nextDialog.onSecondaryAction
    dialog.title = nextDialog.title
    dialog.isActive = true
  }
)

const snackbarColors = {
  success: { snackbar: 'primary', actionButton: 'primary darken-2' },
  error: { snackbar: 'error darken-2', actionButton: 'error darken-3' },
  info: { snackbar: 'primary', actionButton: 'primary darken-2' },
  default: { snackbar: undefined, actionButton: undefined },
}

const secondaryAction = () => {
  dialog.isActive = false
  dialog.onSecondaryAction?.()
}

const confirm = () => {
  dialog.isActive = false
  dialog.onConfirm()
}

const cancel = () => {
  dialog.isActive = false
  dialog.onCancel?.()
}

onBeforeUnmount(() => {
  // Good practice
  onToast.unsubscribe()
  onOpenDialog.unsubscribe()
})
</script>

<style scoped lang="scss"></style>
