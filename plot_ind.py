import requests
  from matplotlib.path import Path
  import matplotlib.patches as patches
  import matplotlib.pyplot as plt

  # Fetch the data for India's coordinates
  url = "https://api.population.io:80/india/"
  response = requests.get(url)

  if response.status_code == 200:
      # Parse the JSON and extract the relevant data
      indian_data = response.json()

      lon, lat = [indian_data["population"][1]["longitude"],
                  indian_data["population"][1]["latitude"]]
  else:
      print(f"Failed to fetch the data: {response.status_code}")

  3. Convert longitude and latitude to coordinates: Use a mapping service or API that
  supports this conversion.
  4. Plot on an online map:

    - Here is a simple example using Google Maps API for plotting points manually (this
  step involves writing a bit of JavaScript):

  // This script will generate a URL for you that you can copy and paste into the
  "Directions" tab in Google Maps or any other service.
  let url = `https://maps.googleapis.com/maps/api/place/nearby_search/json?location=28.61
  3497,77.209015&radius=1000&type=hospital|pharmacy&key=YOUR_API_KEY`;

  fetch(url)
    .then(response => response.json())
    .then(data => {
      data.results.forEach(result => {
        const marker = new google.maps.Marker({
          position: {lat: result.geometry.location.lat(), lng:
  result.geometry.location.lng()},
          map: new google.maps.Map(document.getElementById('map'), {
            center: result.geometry.location,
            zoom: 16
          })
        });
      });
    })
    .catch(error => console.error("There has been a problem with your fetch request:",
  error));


  5. Manual Plotting:

  5. You can use the following steps to plot India's coordinates on a map:

  import matplotlib.pyplot as plt

  plt.figure()
  # Add a pin for India
  ax = plt.gca()  # Get current Axes instance
  circle = plt.Circle((78, 20), 10)  # Make a circle of radius 10 at the center (x=78,
  y=20)
  ax.add_artist(circle)

  plt.show()
