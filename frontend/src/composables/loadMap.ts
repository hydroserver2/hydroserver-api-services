import { Loader } from '@googlemaps/js-api-loader'

type MapOptions = {
  styles?: google.maps.MapTypeStyle[]
}

export const loadMap = async (
  container: HTMLElement,
  mapOptions: MapOptions = {}
) => {
  const loader = new Loader({
    apiKey: import.meta.env.VITE_APP_GOOGLE_MAPS_API_KEY,
  })
  const google = await loader.load()

  const defaultStyles: google.maps.MapTypeStyle[] = [
    {
      featureType: 'poi',
      stylers: [{ visibility: 'off' }],
    },
    {
      featureType: 'transit',
      stylers: [{ visibility: 'off' }],
    },
    {
      featureType: 'landscape',
      elementType: 'labels',
      stylers: [{ visibility: 'off' }],
    },
  ]

  return new google.maps.Map(container, {
    ...mapOptions,
    styles: mapOptions.styles ?? defaultStyles,
  })
}
