markdown
# Subscriber Balance Analysis

## Overview
This project processes transaction logs, analyzes subscriber trends, identifies overdrafts, and detects anomalies. The results are exported to Excel for easy viewing.
The Analysis Part can be further enhanced.
Proposed Data Model according the data in ogs is also available in the Folder Data Model

## Setup

1. **Clone the repository**:
   
   git clone https://github.com/your-repo/subscriber-balance-analysis.git
   cd subscriber-balance-analysis
   

2. **Build and run the Docker container**:
   
   docker build -t subscriber-balance-analysis .
   docker run -v $(pwd)/output:/app/output subscriber-balance-analysis
   

## Implementation Details

- **Python**: For data processing and analysis.
- **pandas**: For data manipulation.
- **CSV files**: For storing transaction data.
- **Docker**: To containerize the application for easy deployment.

## Future Improvements

- **Enhanced Logging**: Include more detailed logs for better traceability.
- **Analysis**: Different type of trend analysis can performed depending upon the business requirements.
- **Scalability**: Transition to a more scalable database like Teradata, MySQL etc. if the data volume increases significantly.


### Running the Solution

1. *Build the Docker Image*:
   bash
   docker build -t subscriber-balance-analysis .
   

2. *Run the Docker Container*:
   docker run subscriber-balance-analysis
   

### Output
The output Excel report will be available in the output/report.xlsx, containing sheets for  transactions, overdrafts,Errered Out transactions with Unsync Balance and anomalies or for further analysis see Visualizations folder.
Logs Data is also avialble in the Processed_Data folder.

This setup ensures that the solution is portable, easy to run on any machine, and generates reports that are easily viewable by non-technical users