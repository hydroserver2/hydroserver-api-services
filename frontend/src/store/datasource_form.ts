import { defineStore } from 'pinia';


type scheduleTypeValues = 'interval' | 'crontab'
type intervalUnitsValues = 'minutes' | 'hours' | 'days'
type columnTypeValues = 'index' | 'name'
type timestampFormatValues = 'iso' | 'custom'

interface DataSourceForm {
  dataSourceId: string | null
  formReady: boolean
  dataLoaders: any[]
  dataSource?: any
  dataSourceName?: string
  dataLoader?: any
  localFilePath?: string
  fileDelimiter: string
  fileHeaderRow?: number
  dataStartRow: number
  scheduleStartTime?: string
  scheduleEndTime?: string
  scheduleType: scheduleTypeValues
  interval?: number
  intervalUnits: intervalUnitsValues
  crontab?: string
  timestampType: columnTypeValues
  timestampColumn?: string | number
  timestampFormat: timestampFormatValues
  timestampCustomFormat?: string
  timestampUseTimezoneOffset: boolean
  timestampTimezoneOffset?: string
}


export const useDataSourceFormStore = defineStore('data-source-form-store', {
  state: (): DataSourceForm => ({
    dataSourceId: null,
    formReady: false,
    dataLoaders: [],
    fileDelimiter: ',',
    dataStartRow: 1,
    scheduleType: 'interval',
    intervalUnits: 'minutes',
    timestampType: 'index',
    timestampFormat: 'iso',
    timestampUseTimezoneOffset: false,
  }),
  actions: {
    async fetchDataSource() {
      if (this.dataSourceId) {
        const dataSource = await this.$http.get(`/data-sources/${this.dataSourceId}`)
        this.dataSource = dataSource.data
      } else {
        this.dataSource = null
      }
    },
    async fetchDataLoaders() {
      const dataLoaders = await this.$http.get('/data-loaders')
      this.dataLoaders = dataLoaders.data
    },
    async saveDataSource() {

      let dataSourceBody

      dataSourceBody = {
        'name': null as string | null | undefined,
        'data_loader': null as string | null,
        'schedule': {} as any,
        'file_access': {} as any,
        'file_timestamp': {} as any,
        'datastreams': [] as any[] | undefined
      }

      dataSourceBody['name'] = this.dataSourceName
      dataSourceBody['data_loader'] = this.dataLoader.id || this.dataLoader
      dataSourceBody['file_access']['path'] = this.localFilePath
      dataSourceBody['file_access']['header_row'] = this.fileHeaderRow || null
      dataSourceBody['file_access']['data_start_row'] = this.dataStartRow || null
      dataSourceBody['file_access']['delimiter'] = this.fileDelimiter || null
      dataSourceBody['schedule']['start_time'] = this.scheduleStartTime || null
      dataSourceBody['schedule']['end_time'] = this.scheduleEndTime || null
      dataSourceBody['schedule']['crontab'] = this.scheduleType === 'crontab' ? this.crontab : null
      dataSourceBody['schedule']['interval'] = this.scheduleType === 'interval' ? this.interval : null
      dataSourceBody['schedule']['interval_units'] = this.scheduleType === 'interval' ? this.intervalUnits : null
      dataSourceBody['file_timestamp']['column'] = this.timestampColumn || null
      dataSourceBody['file_timestamp']['format'] = this.timestampCustomFormat || 'iso'
      dataSourceBody['file_timestamp']['offset'] = this.timestampTimezoneOffset || null

      let response = null

      if (this.dataSourceId) {
        response = await this.$http.patch(
          `/data-sources/${this.dataSourceId}`,
          dataSourceBody
        )
      } else {
        response = await this.$http.post(
          '/data-sources',
          dataSourceBody
        )
      }
      return response?.status === 201 || response?.status === 204;
    },
    fillForm() {
      let dataSource = this.dataSource

      this.dataSourceName = dataSource ? dataSource['name'] : null
      this.dataSource = dataSource ? dataSource['name'] : null
      this.dataLoader = dataSource ? dataSource['data_loader'] : null
      this.localFilePath = dataSource ? dataSource['file_access']['path'] : null
      this.fileHeaderRow = dataSource ? dataSource['file_access']['header_row'] : null
      this.dataStartRow = dataSource ? dataSource['file_access']['data_start_row'] : 1
      this.fileDelimiter = dataSource ? dataSource['file_access']['delimiter'] : ','

      this.scheduleStartTime = dataSource && dataSource['schedule'] ? dataSource['schedule']['start_time'] : null
      this.scheduleEndTime = dataSource && dataSource['schedule'] ? dataSource['schedule']['end_time'] : null
      this.scheduleType = dataSource && dataSource['schedule'] && dataSource['schedule']['interval'] == null ? 'crontab' : 'interval'
      this.interval = dataSource && dataSource['schedule'] ? dataSource['schedule']['interval'] : null
      this.intervalUnits = dataSource && dataSource['schedule'] ? dataSource['schedule']['interval_units'] : 'minutes'
      this.crontab = dataSource && dataSource['schedule'] ? dataSource['schedule']['crontab'] : null

      if (this.scheduleStartTime) {
        this.scheduleStartTime = this.scheduleStartTime.replace('Z', '')
      }

      if (this.scheduleEndTime) {
        this.scheduleEndTime = this.scheduleEndTime.replace('Z', '')
      }

      this.timestampType = dataSource && typeof dataSource['file_timestamp']['column'] === 'string' ? 'name' : 'index'
      this.timestampColumn = dataSource ? dataSource['file_timestamp']['column'] : null
      this.timestampFormat = dataSource && dataSource['file_timestamp']['format'] != 'iso' ? 'custom' : 'iso'
      this.timestampCustomFormat = dataSource && dataSource['file_timestamp']['format'] != 'iso' ? dataSource['file_timestamp']['format'] : null
      this.timestampTimezoneOffset = dataSource ? dataSource['file_timestamp']['offset'] : null
    }
  }
})