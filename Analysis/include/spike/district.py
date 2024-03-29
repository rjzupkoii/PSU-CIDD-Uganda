# district.py
#
# Include file for the spiking.py script that defines the district plotting class.
import datetime
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

import include.common as shared

# This class wraps the functions related to plotting district spike studies
class district:
  mutations = None
  labels = None
  
  def __plot(self, replicates, year, ylabel, title, filename):
    DATES, DISTRICT, INFECTED, WEIGHTED = 2, 3, 4, 8
  
    # Setup to generate the plot
    matplotlib.rc_file('../Scripts/matplotlibrc-line')
    figure, axes = plt.subplots(3, 5)
    figure.suptitle(title, y = 0.94)
    
    # Set a single order for the districts
    districts = self.mutations.District.unique()
  
    # Start by preparing the replicate data that we need to plot
    ymax = max(self.mutations.Frequency)
    for replicate in replicates:
      # Load the data and prepare the dates
      data = pd.read_csv('data/spiking/{}.csv'.format(replicate), header = None)
      data['frequency'] = data[WEIGHTED] / data[INFECTED]
      ymax = max(ymax, max(data.frequency))
      dates = data[DATES].unique().tolist()
      dates = [datetime.datetime(year, 1, 1) + datetime.timedelta(days=x) for x in dates]
  
      # Generate a 15 panel plot while looping over the districts that we have 
      # spiking data for
      row, col = 0, 0
      for district in districts:
        district_id = self.labels[self.labels.Label == district].ID.values[0]
        axes[row, col].plot(dates, data[data[DISTRICT] == district_id].frequency)
        axes[row, col].title.set_text(district)
        row, col = shared.increment(row, col)
          
    # Next, add the know data points to the plots
    row, col = 0, 0
    for district in districts:
      plt.sca(axes[row, col])
      for index, data_row in self.mutations[self.mutations.District == district].iterrows():
        x = datetime.datetime(data_row.Year, 9, 30)
        y = data_row.Frequency
        plt.scatter(x, y, color = 'black', s = 100, zorder = 99)
      row, col = shared.increment(row, col)
          
    # Format the x, y axis and ticks
    for row in range(3):
      for col in range(5):
        axes[row, col].set_ylim([0, ymax])
        axes[row, col].set_xlim([min(dates), max(dates)])
        axes[row, col].xaxis.set_major_formatter(matplotlib.dates.DateFormatter("'%y"))
        if row != 2 and not (row == 1 and col == 4):
          plt.setp(axes[row, col].get_xticklabels(), visible = False)
        if col != 0:
          plt.setp(axes[row, col].get_yticklabels(), visible = False)
          
    # Apply the final figure formatting
    if len(districts) < 15:
      axes[2, 4].set_visible(False)
    plt.setp(axes[2, 0].get_xticklabels()[0], visible = False)
    plt.sca(axes[1, 0])
    plt.ylabel(ylabel)
    plt.sca(axes[2, 2])
    plt.xlabel('Model Year')
    
    # Save the plot
    plt.savefig('plots/{}'.format(filename))
    plt.close()
  
  def process(self, mutation):
    CONFIGURATION, REPLICATE, FILENAME = 0, 3, 2
  
    # Load relevant data
    data = pd.read_csv(shared.REPLICATES_LIST, header = None)
    self.labels = pd.read_csv(shared.DISTRICTS_MAPPING)
    self.mutations = pd.read_csv(shared.MUTATIONS_TEMPLATE.format(mutation))
  
    configurations = []
    shared.progressBar(0, len(data))
    for index, row in data.iterrows():
      try:
        # Skip if this is not a district calibration
        if len(data[data[FILENAME] == row[FILENAME]]) == 1: continue
        
        # Skip if we have already seen this configuration
        if row[CONFIGURATION] in configurations: continue

        # Get the list of replicates associated with this configuration, note that
        # we are assuming that using the configuration id is more reliable to distinguish
        # between configurations than their filename
        replicates = data[data[CONFIGURATION] == row[CONFIGURATION]][REPLICATE]

        # Determine the year of the study, initially studies started in 2009,
        # but as calibration progressed it was changed and added to the YAML filename
        version = None
        parts = row[FILENAME].replace('.yml', '').split('-')
        if len(parts) == 4:
          year, spike, population = 2009, 0.075, float(parts[3])
        elif len(parts) == 6:
          year, spike = int(parts[3]), float(parts[4])
          if 'v' in parts[5]:
            population = float(parts[5][:parts[5].index('v') - 1])
            version = parts[5][parts[5].index('v') + 1:]
          else:
            population = float(parts[5])
        else:
          exit('\nUnrecognized file format: {}'.format(row[FILENAME]))

        # Prepare the filename and title
        title = '{} (spike: {:.1f}%, pop.: {}%)'.format(parts[2].capitalize(), spike * 100.0, int(population * 100.0))
        filename = '{}/uga-{}-{}-{}-{}.png'.format(mutation, parts[2], year, spike, population)
        if version is not None:
          title += ', version {}'.format(version)
          filename = '{}/uga-{}-{}-{}-{}-v{}.png'.format(
            mutation, parts[2], year, spike, population, version)

        # Prepare the plot, note the configuration
        self.__plot(replicates, year, '{} Frequency'.format(mutation), title, filename)
        configurations.append(row[CONFIGURATION])
        shared.progressBar(index, len(data))
      except Exception as ex:
          print('\nError plotting replicate {}, configuration {}'.format(row[REPLICATE], row[FILENAME]))
          print(ex)
    shared.progressBar(len(data), len(data))    
