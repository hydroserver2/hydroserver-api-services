import '@mdi/font/css/materialdesignicons.css'
import '@fortawesome/fontawesome-free/css/all.css'
import 'vuetify/styles'

import { createVuetify, ThemeDefinition } from 'vuetify'
import { VBtn } from 'vuetify/components'
import * as directives from 'vuetify/directives'

import { md3 } from 'vuetify/blueprints'

const theme: ThemeDefinition = {
  dark: false,
  colors: {
    background: '#FFFFFF',
    surface: '#FFFFFF',
    primary: '#0000FF',
    secondary: '#03DAC6',
    error: '#B00020',
    info: '#2196F3',
    success: '#4CAF50',
    warning: '#FB8C00',
  },
}

const textFieldAttrs = {
  density: 'comfortable',
  variant: 'outlined',
  hideDetails: 'auto',
}

export default createVuetify({
  blueprint: md3,
  directives,
  aliases: {
    VBtnPrimary: VBtn,
    VBtnSecondary: VBtn,
    VBtnTertiary: VBtn,
  },
  defaults: {
    VTextField: textFieldAttrs,
    VAutocomplete: textFieldAttrs,
    VTextarea: textFieldAttrs,
    VBtn: {
      color: 'primary',
      variant: 'text',
      rounded: true,
      density: 'comfortable',
    },
    VBtnPrimary: {
      color: 'primary',
      variant: 'flat',
      rounded: true,
      density: 'comfortable',
    },
    VBtnSecondary: {
      color: 'secondary',
      variant: 'flat',
      rounded: true,
      density: 'comfortable',
    },
    VBtnTertiary: {
      rounded: true,
      variant: 'plain',
      density: 'comfortable',
    },
  },
  theme: {
    defaultTheme: 'theme',
    themes: {
      theme,
    },
    variations: {
      colors: ['primary', 'secondary', 'surface'],
      lighten: 6,
      darken: 6,
    },
  },
})
