import { defineStore } from 'pinia';


interface DataSource {
  id: string,
  name: string,
  location: string,
  status: string,
  statusTip: string,
  paused: boolean,
  data_source_thru: string,
  database_thru: string,
  last_sync_successful: boolean,
  last_synced: string,
  next_sync: string,
  linked_datastreams: number
}

interface DataSources {
  [key: string]: DataSource
}


interface DataSourceDashboard {
  dataSources: DataSources
}


export const useDataSourceDashboardStore = defineStore('data-source-store', {
  state: (): DataSourceDashboard => ({
    dataSources: {}
  }),
  getters: {
    dataSourceRows(state) {
      return Object.values(state.dataSources).map(dataSource => {
        return dataSource
      })
    }
  },
  actions: {
    async fetchDataSources() {
      const dataStreams = await this.$http.get('/data-sources')
      this.dataSources = dataStreams.data.reduce((dataSources: any, dataSource: any) => {
        let status
        let statusTip = null
        let databaseThruUpper = dataSource['database_thru_upper'] ? Date.parse(dataSource['database_thru_upper']) : null
        let databaseThruLower = dataSource['database_thru_lower'] ? Date.parse(dataSource['database_thru_lower']) : null
        let dataSourceThru = dataSource['data_source_thru'] ? Date.parse(dataSource['data_source_thru']) : null
        let lastSynced = dataSource['last_synced'] ? Date.parse(dataSource['last_synced']) : null
        let nextSync = dataSource['next_sync'] ? Date.parse(dataSource['next_sync']) : null

        if (
          dataSource['last_synced'] == null
        ) {
          status = 'pending'
        } else if (
          databaseThruUpper === databaseThruLower &&
          databaseThruUpper === dataSourceThru &&
          dataSource['last_sync_successful'] === true
        ) {
          status = 'ok'
        } else if (databaseThruLower == null || databaseThruUpper == null || dataSourceThru == null) {
          status = 'bad'
          statusTip = 'Some datastreams from this data source may not be synced with HydroServer.'
        } else if (
          databaseThruUpper < dataSourceThru
        ) {
          status = 'bad'
          statusTip = 'This data source is not synced with HydroServer.'
        } else if (
          databaseThruLower < databaseThruUpper
        ) {
          status = 'bad'
          statusTip = 'Some datastreams from this data source are not synced with HydroServer.'
        } else if (dataSource['last_sync_successful'] === false) {
          status = 'bad'
          statusTip = 'Last data loading job failed.'
        } else {
          status = 'unknown'
        }

        dataSources[dataSource['id']] = {
          id: dataSource['id'],
          name: dataSource['name'],
          location: dataSource['file_access']['path'],
          status: status,
          statusTip: statusTip,
          paused: dataSource['schedule']['paused'],
          data_source_thru: dataSourceThru ? new Date(dataSourceThru).toUTCString() : null,
          database_thru: databaseThruUpper ? new Date(databaseThruUpper).toUTCString() : null,
          last_sync_successful: dataSource['last_sync_successful'],
          last_synced: lastSynced ? new Date(lastSynced).toUTCString() : null,
          next_sync: nextSync ? new Date(nextSync).toUTCString() : null,
          linked_datastreams: dataSource['datastreams'].length
        }
        return dataSources
      }, {})
    },
  }
})
