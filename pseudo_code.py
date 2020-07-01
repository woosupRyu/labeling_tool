def process_check(category_id):
    """
    Object table의 (category_id)가 입력받은 값을 가지고 (mix_num)이 -1인 Object table이 존재하고
    해당하는 모든 Object table에 대해 Bbox table과 Mask table이 존재할 경우 True 반환
    이외의 경우 False 반환
    Args:
        category_id (str): Object table의 (category_id)
    Return:
        True, False (Boolean)
    """
