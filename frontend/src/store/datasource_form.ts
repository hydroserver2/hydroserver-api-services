import { defineStore } from 'pinia';


type modeValues = 'create' | 'edit'
type dataSourceTypeValues = 'local' | 'remote'
type scheduleTypeValues = 'interval' | 'crontab'
type intervalUnitsValues = 'minutes' | 'hours' | 'days'
type columnTypeValues = 'index' | 'name'
type timestampFormatValues = 'iso' | 'custom'

interface DataSourceForm {
  datastreamId: string | null
  mode: modeValues
  dataSourceName?: string
  dataSource?: string
  dataSourceType: dataSourceTypeValues
  localFilePath?: string
  remoteFileUrl?: string
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
  datastreamType: columnTypeValues
  datastreamColumn?: string | number
  dataSources: any[]
}


export const useDataSourceFormStore = defineStore('data-source-store', {
  state: (): DataSourceForm => ({
    datastreamId: null,
    mode: 'create',
    dataSourceType: 'local',
    dataStartRow: 1,
    scheduleType: 'interval',
    intervalUnits: 'minutes',
    timestampType: 'index',
    timestampFormat: 'iso',
    timestampUseTimezoneOffset: false,
    datastreamType: 'index',
    dataSources: []
  }),
  actions: {
    async fetchDataSources() {
      const dataStreams = await this.$http.get('/data-sources')
      this.dataSources = dataStreams.data
    },
    async saveDataSource() {

      let dataSourceBody = {
        'name': null as string | null | undefined,
        'schedule': {} as any,
        'file_access': {} as any,
        'file_timestamp': {} as any,
        'datastreams': [] as any[]
      }

      dataSourceBody['name'] = this.dataSourceName
      dataSourceBody['file_access']['path'] = this.dataSourceType === 'local' ? this.localFilePath : null
      dataSourceBody['file_access']['url'] = this.remoteFileUrl === 'remote' ? this.remoteFileUrl : null
      dataSourceBody['file_access']['header_row'] = this.fileHeaderRow || null
      dataSourceBody['file_access']['data_start_row'] = this.dataStartRow || null
      dataSourceBody['schedule']['start_time'] = this.scheduleStartTime || null
      dataSourceBody['schedule']['end_time'] = this.scheduleEndTime || null
      dataSourceBody['schedule']['crontab'] = this.scheduleType === 'crontab' ? this.crontab : null
      dataSourceBody['schedule']['interval'] = this.scheduleType === 'interval' ? this.interval : null
      dataSourceBody['schedule']['interval_units'] = this.scheduleType === 'interval' ? this.intervalUnits : null
      dataSourceBody['file_timestamp']['column'] = this.timestampColumn || null
      dataSourceBody['file_timestamp']['format'] = this.timestampCustomFormat || 'iso'
      dataSourceBody['file_timestamp']['offset'] = this.timestampTimezoneOffset || null

      dataSourceBody['datastreams'].push(
        {
          'column': this.datastreamColumn,
          'datastream_id': this.datastreamId
        }
      )

      let response = null

      if (this.mode === 'create') {
        response = await this.$http.post(
          '/data-sources',
          dataSourceBody
        )
      } else if (this.mode === 'edit') {
        let dataSource = this.dataSources.filter(ds => ds.name === this.dataSource)[0]
        response = await this.$http.patch(
          `/data-sources/${dataSource['id']}`,
          dataSourceBody
        )
      }
      if (response?.status === 201 || response?.status === 204) {
        return true
      } else {
        console.log(response)
        return false
      }
    },
    loadDataSource() {
      let dataSource = this.dataSources.filter(ds => ds.name === this.dataSource)[0]

      this.dataSourceType = dataSource && dataSource['file_access']['path'] == null ? 'remote' : 'local'
      this.localFilePath = dataSource ? dataSource['file_access']['path'] : null
      this.remoteFileUrl = dataSource ? dataSource['file_access']['url'] : null
      this.fileHeaderRow = dataSource ? dataSource['file_access']['header_row'] : null
      this.dataStartRow = dataSource ? dataSource['file_access']['data_start_row'] : 1

      this.scheduleStartTime = dataSource && dataSource['schedule'] ? dataSource['schedule']['start_time'] : null
      this.scheduleStartTime = dataSource && dataSource['schedule'] ? dataSource['schedule']['end_time'] : null
      this.scheduleType = dataSource && dataSource['schedule'] && dataSource['schedule']['interval'] == null ? 'crontab' : 'interval'
      this.interval = dataSource && dataSource['schedule'] ? dataSource['schedule']['interval'] : null
      this.intervalUnits = dataSource && dataSource['schedule'] ? dataSource['schedule']['interval_units'] : 'minutes'
      this.crontab = dataSource && dataSource['schedule'] ? dataSource['schedule']['crontab'] : null

      this.timestampType = dataSource && typeof dataSource['file_timestamp']['column'] === 'string' ? 'name' : 'index'
      this.timestampColumn = dataSource ? dataSource['file_timestamp']['column'] : null
      this.timestampFormat = dataSource && dataSource['file_timestamp']['format'] != null ? 'custom' : 'iso'
      this.timestampCustomFormat = dataSource ? dataSource['file_timestamp']['format'] : null
      this.timestampTimezoneOffset = dataSource ? dataSource['file_timestamp']['offset'] : null

      let datastreamColumn = (((dataSource || {})['datastreams'] || []).filter(
        (ds: any) => ds['datastream_id'] === this.datastreamId
      )[0] || {}).column

      this.datastreamType = this.datastreamId !== null && datastreamColumn !== undefined && typeof datastreamColumn === 'string' ? 'name' : 'index'
      this.datastreamColumn = this.datastreamId !== null && datastreamColumn !== undefined ? datastreamColumn : null
    }
  }
})