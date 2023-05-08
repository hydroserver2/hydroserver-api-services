declare module '*.vue' {
  import { defineComponent } from 'vue'
  const Component: ReturnType<typeof defineComponent>
  interface ComponentCustomProperties {
    $http: typeof axios
  }
  export default Component
}
