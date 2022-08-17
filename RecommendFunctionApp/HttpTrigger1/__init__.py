import logging
import azure.functions as func
import pickle
from io import BytesIO
import json
 

# Use Azure main function to get the recommendations
def main(
    req: func.HttpRequest, 
    popularityTable: func.InputStream, 
    recommendationsTable: func.InputStream) -> func.HttpResponse:
    
    logging.info('Python HTTP trigger function processed a request.')

    # Load the data from AzureBlobStorage 
    popularity_rec = pickle.load(BytesIO(popularityTable.read()))
    print('popularity_rec: ', len(popularity_rec))
    
    
    recommendations_rec = pickle.load(BytesIO(recommendationsTable.read()))
    print('recommendations_rec: ', len(recommendations_rec))

    # Get the sample_user_id param (see the Frontend app for the request structure)
    sample_user_id = req.params.get('data')
    
    if not sample_user_id:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            sample_user_id = req_body.get('data')

    if sample_user_id:
        # Get the top 5 recommendation for user id
        sample_user_id = int(sample_user_id)
        
        # if sample_user_id belongs to the recommendations dictionary keys, then get the recommendations from there
        # otherwise get the top5 recommendations
        top5rec     = popularity_rec[:5]
        top5message = "most popular articles"
        
        if sample_user_id in recommendations_rec.keys():
            top5message = "CF recommendations ignoring user already visited articles."
            top5rec = recommendations_rec[sample_user_id]
        
        # to avoid np.ndarray conversion error, and int64 conversion error during json.dumps, let's translate the recommendations into a simple python list
        top5rec = [int(article_id) for article_id in top5rec]
        response_data = json.dumps({"result": top5rec , "message": top5message})
 
        # Return the recommendation
        return func.HttpResponse(response_data, status_code=200)

    else:
        response_data = json.dumps({"error": "the function should be called with a data parameter containing an integer user ID"})
        return func.HttpResponse(
             response_data, 
             status_code=200)