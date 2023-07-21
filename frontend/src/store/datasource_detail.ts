import { defineStore } from 'pinia';


interface DatastreamDetail {
  id: string
  name: string
  status: string
  dataThru?: string
  column: string | number
}

interface DataSourceDetail {
  id?: string
  name?: string
  status?: string
  paused?: string
  dataLoader?: string
  filePath?: string
  headerRow?: number
  dataStartRow?: number
  scheduleStartTime?: string
  scheduleEndTime?: string
  scheduleValue?: string
  timestampFormat?: string
  timestampColumn?: string | number
  timezoneOffset?: string
  datastreams?: DatastreamDetail[]
  lastSyncSuccessful?: boolean
  lastSyncMessage?: string
  lastSynced?: string
  nextSync?: string
  dataSourceThru?: string
}


export const useDataSourceDetailStore = defineStore('data-source-detail-store', {
  state: (): DataSourceDetail => ({}),
  actions: {
    async fetchDataSource() {
      let response = await this.$http.get(`/data-sources/${this.id}`)
      let dataSource = response.data

      let now = new Date()
      let scheduleStartTime = (dataSource.schedule || {}).start_time ? new Date(Date.parse(dataSource.schedule.start_time)) : null
      let scheduleEndTime = (dataSource.schedule || {}).end_time ? new Date(Date.parse(dataSource.schedule.end_time)) : null
      let databaseThruUpper = dataSource.database_thru_upper ? new Date(Date.parse(dataSource.database_thru_upper)) : null
      let databaseThruLower = dataSource.database_thru_lower ? new Date(Date.parse(dataSource.database_thru_lower)) : null
      let dataSourceThru = dataSource.data_source_thru ? new Date(Date.parse(dataSource.data_source_thru)) : null
      let lastSynced = dataSource.last_synced ? new Date(Date.parse(dataSource.last_synced)) : null
      let nextSync = dataSource.next_sync ? new Date(Date.parse(dataSource.next_sync)) : null

      this.name = dataSource.name
      this.dataLoader = (dataSource.data_loader || {}).name
      this.filePath = (dataSource.file_access || {}).path
      this.headerRow = (dataSource.file_access || {}).header_row
      this.dataStartRow = (dataSource.file_access || {}).data_start_row

      this.scheduleStartTime = scheduleStartTime ? scheduleStartTime.toUTCString() : undefined
      this.scheduleEndTime = scheduleEndTime ? scheduleEndTime.toUTCString() : undefined
      this.paused = (dataSource.schedule || {}).paused ? 'True' : 'False'

      if ((dataSource.schedule || {}).crontab) {
        this.scheduleValue = `Crontab: ${dataSource.schedule.crontab}`
      } else if ((dataSource.schedule || {}).interval_units) {
        this.scheduleValue = `Every ${dataSource.schedule.interval} ${dataSource.schedule.interval_units}`
      }

      this.timestampFormat = (dataSource.file_timestamp || {}).format === 'iso' ? 'ISO' : (dataSource.file_timestamp || {}).format
      this.timestampColumn = (dataSource.file_timestamp || {}).column
      this.timezoneOffset = (dataSource.file_timestamp || {}).offset

      this.lastSyncSuccessful = dataSource.last_sync_successful
      this.lastSyncMessage = dataSource.last_sync_message
      this.lastSynced = lastSynced ? lastSynced.toUTCString() : undefined
      this.nextSync = nextSync ? nextSync.toUTCString() : undefined
      this.dataSourceThru = dataSourceThru ? dataSourceThru.toUTCString() : undefined

      if (
        lastSynced == null
      ) {
        this.status = 'Pending'
      } else if (
        databaseThruUpper === databaseThruLower &&
        databaseThruUpper === dataSourceThru &&
        dataSource['last_sync_successful'] === true &&
        nextSync && nextSync >= now
      ) {
        this.status = 'Up-To-Date'
      } else if (databaseThruLower == null || databaseThruUpper == null || dataSourceThru == null) {
        this.status = 'Needs Attention'
      } else if (
        databaseThruUpper < dataSourceThru
      ) {
        this.status = 'Needs Attention'
      } else if (
        databaseThruLower < databaseThruUpper
      ) {
        this.status = 'Needs Attention'
      } else if (dataSource['last_sync_successful'] === false) {
        this.status = 'Needs Attention'
      } else if (
        nextSync &&
        nextSync < now
      ) {
        this.status = 'Behind Schedule'
      } else {
        this.status = 'Unknown'
      }

      this.datastreams = (dataSource.datastreams || []).map((datastream: any) => {
        let dataThru = datastream.result_end_time ? new Date(Date.parse(datastream.result_end_time)) : null
        let status

        if (!dataThru && !dataSourceThru) {
          status = 'Pending'
        } else if (dataThru && dataSourceThru && dataThru >= dataSourceThru) {
          status = 'Up-To-Date'
        } else {
          status = 'Needs Attention'
        }

        return {
          id: datastream.id,
          name: datastream.name,
          status: status,
          dataThru: dataThru ? dataThru.toUTCString() : undefined,
          column: datastream.column
        }
      })

    }
  }
})
