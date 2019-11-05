### Recommending Packages of Multi-Criteria Items to Groups

This is the source code for the model implementations from the paper:

Ceh-Varela, E., & Cao, H. (2019, July). Recommending Packages of Multi-Criteria Items to Groups. In 2019 IEEE International Conference on Web Services (ICWS) (pp. 273-282). IEEE.

### Project Structure
+ datasets (Datasets for the TripAdvisor's catetories)
    
    +  Category 1: Restaurant, Category 2: Hotel
 
+ model (Source files for different modules)

+ packages (Placeholder for the final resulting packages)

+ parameters (Different parameters used by the modules)
    + common_parameters.py

+ temp (Placeholder for auxiliary files generated during execution)

+ logs (Placeholder for final metrics results used for the paper's figures)

### Example of execution

+  python run.py

+ each file inside the "model" folder could be run independently in the following order.

    + To generate the auxiliary data (these scripts should be run before the models or baselines).
    An example is the following:
    
        + python Extract_Biclusters.py -o 1 -x 5 -y 4
        + python CC_Utils.py -o 1
        + python Get_Items_Based_UF.py -o 1 -kitems 20
        + python Get_SIM_i_f.py -o 1
        + python 'Find_UI_items.py -o 1
        + python Get_CC_U-I_Belong.py -o 1
        + python I-I-CF.py -o 1 -G 158,204,41,98
        + python U-U-CF.py -o 1 -G 158,204,41,98
        + pytho Predict_Ratings.py -o 1 -alpha 0.6
        + python Build_Dense_Matrix.py -o 1 -kitems 20 -G 58,204,41,98
        
    + After running the above scripts for all categories (i.e., '-o 1', and '-o 2')
        + python Get_POC.py -o all -G 58,204,41,98
        + Extract_User_Preferences.py -o all -agg 5 --pt 0
        
    + To run the models
        + python Model1.py -o all -agg 5 --pt 0
        + python Model2.py -o all -agg 5 --pt 0
        
    + To run the baselines
        + python Fairness_baseline -o all --kitems 20
        + python Average_baseline -o all --kitems 20
        + python GRmodel_baseline -o all --kitems 20
        
    + To run the metrics
        + python Consensus_metric.py
        + python m_envy_metric.py
        
