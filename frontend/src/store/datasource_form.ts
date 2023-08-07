import { defineStore } from 'pinia';


type modeValues = 'create' | 'edit'
type scheduleTypeValues = 'interval' | 'crontab'
type intervalUnitsValues = 'minutes' | 'hours' | 'days'
type columnTypeValues = 'index' | 'name'
type timestampFormatValues = 'iso' | 'custom'

interface DataSourceForm {
  datastreamId: string | null
  dataSourceId: string | null
  formReady: boolean
  formMode: modeValues
  dataSourceName?: string
  dataSource?: any
  dataLoader?: any
  localFilePath?: string
  fileHeaderRow?: number
  dataStartRow: number
  scheduleStartTime?: string
  scheduleEndTime?: string
  scheduleType: scheduleTypeValues
  interval?: number
  intervalUnits: intervalUnitsValues
  crontab?: string
  paused: boolean
  timestampType: columnTypeValues
  timestampColumn?: string | number
  timestampFormat: timestampFormatValues
  timestampCustomFormat?: string
  timestampUseTimezoneOffset: boolean
  timestampTimezoneOffset?: string
  datastreamType: columnTypeValues
  datastreamColumn?: string | number
  datastreamColumns: any[]
  dataSources: any[]
  dataLoaders: any[]
  // datastreams: any[]
}


export const useDataSourceFormStore = defineStore('data-source-form-store', {
  state: (): DataSourceForm => ({
    datastreamId: null,
    dataSourceId: null,
    formReady: false,
    formMode: 'create',
    dataStartRow: 1,
    scheduleType: 'interval',
    intervalUnits: 'minutes',
    paused: false,
    timestampType: 'index',
    timestampFormat: 'iso',
    timestampUseTimezoneOffset: false,
    datastreamType: 'index',
    datastreamColumns: [],
    dataSources: [],
    dataLoaders: [],
    // datastreams: []
  }),
  // getters: {
  //   datastreamRows(): any {
  //     return this.datastreams.map((datastream: any) => {
  //       return {
  //         column: (this.datastreamColumns.filter(column => column.id === datastream.id)[0] || {}).column,
  //         ...datastream
  //       }
  //     })
  //   }
  // },
  actions: {
    async fetchDataSources() {
      const dataStreams = await this.$http.get('/data-sources')
      this.dataSources = dataStreams.data
    },
    async fetchDataLoaders() {
      const dataLoaders = await this.$http.get('/data-loaders')
      this.dataLoaders = dataLoaders.data
    },
    async fetchDatastreams() {
      const datastreams = await this.$http.get('/datastreams')
      // this.datastreams = datastreams.data
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
      dataSourceBody['schedule']['start_time'] = this.scheduleStartTime || null
      dataSourceBody['schedule']['end_time'] = this.scheduleEndTime || null
      dataSourceBody['schedule']['crontab'] = this.scheduleType === 'crontab' ? this.crontab : null
      dataSourceBody['schedule']['interval'] = this.scheduleType === 'interval' ? this.interval : null
      dataSourceBody['schedule']['interval_units'] = this.scheduleType === 'interval' ? this.intervalUnits : null
      dataSourceBody['schedule']['paused'] = this.paused
      dataSourceBody['file_timestamp']['column'] = this.timestampColumn || null
      dataSourceBody['file_timestamp']['format'] = this.timestampCustomFormat || 'iso'
      dataSourceBody['file_timestamp']['offset'] = this.timestampTimezoneOffset || null

      // if (!this.datastreamId) {
      //   dataSourceBody['datastreams'] = this.datastreamColumns
      // } else {
      //   dataSourceBody['datastreams']?.push(
      //     {
      //       'column': this.datastreamColumn,
      //       'datastream_id': this.datastreamId
      //     }
      //   )
      // }

      if (this.datastreamId) {
        dataSourceBody['datastreams'] =  this.datastreamColumns as any[] | undefined
        dataSourceBody['datastreams'] = dataSourceBody['datastreams']?.filter(
          datastream => datastream['id'] != this.datastreamId
        )
        dataSourceBody['datastreams']?.push({
          'column': this.datastreamColumn || null,
          'id': this.datastreamId
        })
      }

      console.log('$$$$$')
      console.log(dataSourceBody)

      let response = null

      if (this.formMode === 'create') {
        response = await this.$http.post(
          '/data-sources',
          dataSourceBody
        )
      } else if (this.formMode === 'edit') {
        let dataSource = this.dataSources.filter(ds => ds.name === this.dataSource)[0]
        response = await this.$http.patch(
          `/data-sources/${dataSource['id']}`,
          dataSourceBody
        )
      }
      return response?.status === 201 || response?.status === 204;
    },
    fillForm() {
      let dataSource = null

      if (this.datastreamId) {
        dataSource = this.dataSources.filter(datasource => {
          return datasource.datastreams.filter((datastream: any) => this.datastreamId === datastream.id).length > 0
        })[0] || null
      } else if (this.dataSourceId) {
        dataSource = this.dataSources.filter(ds => ds.id === this.dataSourceId)[0] || null
      }

      if (dataSource == null) {
        this.formMode = 'create'
      } else {
        this.formMode = 'edit'
      }

      this.dataSourceName = dataSource ? dataSource['name'] : null
      this.dataSource = dataSource ? dataSource['name'] : null
      this.dataLoader = dataSource ? dataSource['data_loader'] : null
      this.localFilePath = dataSource ? dataSource['file_access']['path'] : null
      this.fileHeaderRow = dataSource ? dataSource['file_access']['header_row'] : null
      this.dataStartRow = dataSource ? dataSource['file_access']['data_start_row'] : 1

      this.scheduleStartTime = dataSource && dataSource['schedule'] ? dataSource['schedule']['start_time'] : null
      this.scheduleStartTime = dataSource && dataSource['schedule'] ? dataSource['schedule']['end_time'] : null
      this.scheduleType = dataSource && dataSource['schedule'] && dataSource['schedule']['interval'] == null ? 'crontab' : 'interval'
      this.interval = dataSource && dataSource['schedule'] ? dataSource['schedule']['interval'] : null
      this.intervalUnits = dataSource && dataSource['schedule'] ? dataSource['schedule']['interval_units'] : 'minutes'
      this.crontab = dataSource && dataSource['schedule'] ? dataSource['schedule']['crontab'] : null
      this.paused = dataSource && dataSource['schedule'] ? dataSource['schedule']['paused'] : false

      this.timestampType = dataSource && typeof dataSource['file_timestamp']['column'] === 'string' ? 'name' : 'index'
      this.timestampColumn = dataSource ? dataSource['file_timestamp']['column'] : null
      this.timestampFormat = dataSource && dataSource['file_timestamp']['format'] != null ? 'custom' : 'iso'
      this.timestampCustomFormat = dataSource ? dataSource['file_timestamp']['format'] : null
      this.timestampTimezoneOffset = dataSource ? dataSource['file_timestamp']['offset'] : null

      this.datastreamColumns = ((dataSource || {}).datastreams || []).map((datastream: any) => {
        return {
          id: datastream.id,
          column: datastream.column
        }
      })

      if (this.datastreamId) {
        this.datastreamColumn = (this.datastreamColumns.filter(
          column => column.id === this.datastreamId
        )[0] || {}).column
      }
    }
  }
})