from collections                                import namedtuple
from typing                                     import Optional
import numpy        as np
import math
import cv2
import base64
import re

class algothihm:
    def __init__(self,dataset):
        """
        dataset = {
            "inner" : b64data,
            "outer" : b64data
        }
        // for rotate captcha

        dataset = {
            "bigimage" : ""
        }
        """
        self.dataset = {} #picture data
        for i in dataset:
            self.dataset[i] = {
                    "b64" : dataset[i],
                    "image" : self.decode_base64(dataset[i])
                }

    def image_to_base64(self,image_path):
        image = cv2.imread(image_path)
        _, encoded_image = cv2.imencode('.png', image)
        base64_string = base64.b64encode(encoded_image.tobytes()).decode('utf-8')
        return base64_string
    
    def decode_base64(self,base64_string):
        img_data = base64.b64decode(base64_string)
        img_np = np.frombuffer(img_data, dtype=np.uint8)
        img = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
        return img
    
    def resize_image(self,image, target_width, target_height):
        return cv2.resize(image, (target_width, target_height))
    
    def rotate_image(self,image, angle):
        height, width = image.shape[:2]
        center = (width // 2, height // 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated_image = cv2.warpAffine(image, rotation_matrix, (width, height))
        return rotated_image


    def rotate(self):
        RotateData = namedtuple("RotateData", "similar, angle, start, end, step")
        MatchData = namedtuple("MatchData", "similar, inner_rotate_angle, total_rotate_angle")
        def request_image_content(image_url, proxies: Optional[dict] = None):
            import requests
            headers = {
                "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
            }
            response = requests.get(image_url, headers=headers, proxies=proxies)
            return response.content
        
        def set_mask(radius, check_pixel):
            center_point = (radius, radius)
            mask = np.zeros((radius * 2, radius * 2), dtype=np.uint8)
            mask = cv2.circle(mask, center_point, radius, (255, 255, 255), -1)
            mask = cv2.circle(mask, center_point, radius - check_pixel, (0, 0, 0), -1)
            return mask
        
        def cut_image(origin_array, radius=None, check_pixel=None):
            cut_pixel_list = []
            height, width = origin_array.shape[:2]
            if not radius:
                for rotate_count in range(4):
                    cut_pixel = 0
                    rotate_array = np.rot90(origin_array, rotate_count)
                    for line in rotate_array:
                        pixel_set = (
                            set(list(line)) if len(line.shape) == 1 else set(map(tuple, line))
                        )
                        if not pixel_set.issubset({0, 255, (0, 0, 0), (255, 255, 255)}):
                            break
                        cut_pixel += 1
                    cut_pixel_list.append(cut_pixel)
                cut_pixel_list[2] = height - cut_pixel_list[2]
                cut_pixel_list[3] = width - cut_pixel_list[3]
            elif check_pixel:
                y, x = height // 2, width // 2
                resize_check_pixel = math.ceil(radius / (radius - check_pixel) * check_pixel)
                for i in -1, 1:
                    for p in y, x:
                        pos = p + i * radius
                        for _ in range(p - radius):
                            p_x, p_y = (pos, y) if len(cut_pixel_list) % 2 else (x, pos)
                            pixel_point = origin_array[p_x][p_y]
                            pixel_set = (
                                {pixel_point}
                                if isinstance(pixel_point, np.uint8)
                                else set(pixel_point)
                            )
                            if not pixel_set.issubset({0, 255}):
                                break
                            pos += i
                        cut_pixel_list.append(pos + i * resize_check_pixel)
            up, left, down, right = cut_pixel_list
            cut_array = origin_array[up:down, left:right]
            diameter = (radius or min(cut_array.shape[:2]) // 2) * 2
            cut_result = cv2.resize(cut_array, dsize=(diameter, diameter))
            return cut_result
        
        def mask_image(origin_array, check_pixel):
            radius = origin_array.shape[0] // 2
            mask = set_mask(radius, check_pixel)
            src_array = np.zeros(origin_array.shape, dtype=np.uint8)
            mask_result = cv2.add(origin_array, src_array, mask=mask)
            return mask_result
        
        def rotate_image(inner_image, outer_image, anticlockwise):
            rotate_info_list = [RotateData(0, 0, 1, 361, 10)]
            rtype = int(anticlockwise) or -1
            h, w = inner_image.shape[:2]
            for item in rotate_info_list:
                min_similar_rotate_info = item
                for angle in range(*item[2:]):
                    mat_rotate = cv2.getRotationMatrix2D((h * 0.5, w * 0.5), rtype * angle, 1)
                    dst = cv2.warpAffine(inner_image, mat_rotate, (h, w))
                    ret = cv2.matchTemplate(outer_image, dst, cv2.TM_CCOEFF_NORMED)
                    similar_value = cv2.minMaxLoc(ret)[1]
                    if similar_value < min_similar_rotate_info.similar:
                        continue
                    rotate_info = RotateData(similar_value, angle, angle - 10, angle + 10, 10)
                    rotate_info_list.append(rotate_info)
                    if len(rotate_info_list) > 5:
                        rotate_info_list.remove(min_similar_rotate_info)
                    min_similar_rotate_info = min(rotate_info_list)
            return max(rotate_info_list)
        
        def image_to_cv2(base_image: str, image_type: int, grayscale: bool, proxies=None):
            assert image_type in [0, 1, 2]
            if image_type == 0:
                search_base64 = re.search("base64,(.*?)$", base_image)
                base64_image = search_base64.group(1) if search_base64 else base_image
                image_array = np.asarray(bytearray(base64.b64decode(base64_image)), dtype="uint8")
                image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            elif image_type == 1:
                image_content = request_image_content(base_image, proxies)
                if not image_content:
                    raise Exception("Da co loi xay ra！")
                image_array = np.array(bytearray(image_content), dtype=np.uint8)
                image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            else:
                image = cv2.imread(base_image)
            if grayscale:
                image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            return image
        
        def rotate_identify(small_circle: str,big_circle: str,image_type: int = 0,check_pixel: int = 10,speed_ratio: float = 1,grayscale: bool = False,anticlockwise: bool = False,proxies: Optional[dict] = None,) -> MatchData:
            inner_image = image_to_cv2(small_circle, image_type, grayscale, proxies)
            outer_image = image_to_cv2(big_circle, image_type, grayscale, proxies)
            cut_inner_image = cut_image(inner_image)
            cut_inner_radius = cut_inner_image.shape[0] // 2
            cut_outer_image = cut_image(outer_image, cut_inner_radius, check_pixel)
            inner_annulus = mask_image(cut_inner_image, check_pixel)
            outer_annulus = mask_image(cut_outer_image, check_pixel)
            rotate_info = rotate_image(inner_annulus, outer_annulus, anticlockwise)
            inner_angle = round(rotate_info.angle * speed_ratio / (speed_ratio + 1), 2)
            return MatchData(rotate_info.similar, inner_angle, rotate_info.angle)
        
        small_circle = self.dataset["innerImageB64"]["b64"]#self.image_to_base64(self.dataset[0])
        big_circle = self.dataset["outerImageB64"]["b64"]#self.image_to_base64(self.dataset[1])
        angle = rotate_identify(small_circle, big_circle)
        small_circle = self.rotate_image(self.decode_base64(small_circle),-angle[1])
        big_circle = self.rotate_image(self.decode_base64(big_circle),angle[1])
        return angle[1]
    
    def slider(self):
        def image_to_cv2(image: str, grayscale: bool):
            if grayscale:
                image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            return image
        
        ####################JUANE###############
        slider_img = image_to_cv2(self.dataset["pieceImageB64"]["image"],True)
        background_img = image_to_cv2(self.dataset["puzzleImageB64"]["image"], True)
        background_edge = cv2.Canny(background_img, 100, 200)
        slider_edge = cv2.Canny(slider_img, 100, 200)
        background_pic = cv2.cvtColor(background_edge, cv2.COLOR_GRAY2RGB)
        slider_pic = cv2.cvtColor(slider_edge, cv2.COLOR_GRAY2RGB)
        res = cv2.matchTemplate(background_pic, slider_pic, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        height, width       = self.dataset["puzzleImageB64"]["image"].shape[:2]
        return max_loc[0] / width
        ###################CHATGPT#########################
        # image1              = self.dataset["pieceImageB64"]["image"]
        # gray1               = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
        # edges1              = cv2.Canny(cv2.GaussianBlur(gray1, (5, 5), 0), 50, 150)
        # contours1, _        = cv2.findContours(edges1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # largest_contour1    = max(contours1, key=cv2.contourArea)
        # image2              = self.dataset["puzzleImageB64"]["image"]
        # gray2               = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
        # edges2              = cv2.Canny(cv2.GaussianBlur(gray2, (5, 5), 0), 50, 150)
        # contours2, _        = cv2.findContours(edges2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # closest_contour2    = min(contours2, key=lambda c2: cv2.matchShapes(largest_contour1, c2, 1, 0.0))
        # x, y, w, h          = cv2.boundingRect(closest_contour2)
        # height, width       = self.dataset["puzzleImageB64"]["image"].shape[:2]
        # center_square       = x + w // 2
        # print("solution", (width, center_square, center_square/width))
        # return center_square / width
        # def __sobel_operator(img):
        #     scale = 1
        #     delta = 0
        #     ddepth = cv2.CV_16S
        #     img = cv2.GaussianBlur(img, (3, 3), 0)
        #     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        #     grad_x = cv2.Sobel(gray,ddepth,1,0,ksize=3,scale=scale,delta=delta,borderType=cv2.BORDER_DEFAULT,)
        #     grad_y = cv2.Sobel(gray,ddepth,0,1,ksize=3,scale=scale,delta=delta,borderType=cv2.BORDER_DEFAULT,)
        #     abs_grad_x = cv2.convertScaleAbs(grad_x)
        #     abs_grad_y = cv2.convertScaleAbs(grad_y)
        #     grad = cv2.addWeighted(abs_grad_x, 0.5, abs_grad_y, 0.5, 0)
        #     return grad
        ################## TEKKY ####################
        # puzzle = __sobel_operator(
        #     cv2.imdecode(
        #         np.frombuffer(
        #             base64.b64decode(self.dataset["pieceImageB64"]["b64"]),
        #             dtype="uint8"
        #         ),
        #         cv2.IMREAD_COLOR
        #     )
        # )
        # piece = __sobel_operator(
        #     cv2.imdecode(
        #         np.frombuffer(
        #             base64.b64decode(self.dataset["puzzleImageB64"]["b64"]),
        #             dtype="uint8"
        #         ),
        #         cv2.IMREAD_COLOR
        #     )
        # )
        # matched = cv2.matchTemplate(
        #     puzzle, 
        #     piece, 
        #     cv2.TM_CCOEFF_NORMED
        # )
        # min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(matched)
        # height, width       = self.dataset["puzzleImageB64"]["image"].shape[:2]
        # print("algorith good", (max_loc[0], width, max_loc[0]/width))
        # return max_loc[0] / width
    
    def similar(self):
        def scale(size0, size1, pos):
            ratio_width = size1[0] / size0[0]
            ratio_height = size1[1] / size0[1]
            point_1 = pos[0]
            point_2 = pos[1]
            point_1 = (round(point_1[0]*ratio_height), round(point_1[1]*ratio_width))
            point_2 = (round(point_2[0]*ratio_height), round(point_2[1]*ratio_width))
            return point_1, point_2
        
        def blue(img):
            img_thr_blue = cv2.inRange(img,(95,150,200),(160,210,255))
            contours1 = cv2.findContours(img_thr_blue, 
                    cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            list_ = []
            for con in contours1[0]:
                if (cv2.contourArea(con) >300):
                    x,y,w,h = cv2.boundingRect(con)
                    x1,y1,x2,y2 = x,y, x+w ,y+h
                    list_.append([x1,y1,x2,y2])
            return list_
            
        def green(img):    
            img_thr_green = cv2.inRange(img,(140,160,120),(180,230,180))&(img[:,:,1]-img[:,:,0]>30)&(img[:,:,1]-img[:,:,2]>30)
            contours1 = cv2.findContours(img_thr_green, 
                    cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            list_ = []
            for con in contours1[0]:
                if (cv2.contourArea(con) >300):
                    x,y,w,h = cv2.boundingRect(con)
                    x1,y1,x2,y2 = x,y, x+w ,y+h
                    list_.append([x1,y1,x2,y2])
            return list_
            
        def red(img):   
            img_thr_red = cv2.inRange(img,(220,150,130),(255,200,160))&(img[:,:,0]-img[:,:,1]>30)&(img[:,:,1]>img[:,:,2])
            contours1 = cv2.findContours(img_thr_red, 
                    cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            list_ = []
            for con in contours1[0]:
                if (cv2.contourArea(con) >300):
                    x,y,w,h = cv2.boundingRect(con)
                    x1,y1,x2,y2 = x,y, x+w ,y+h
                    list_.append([x1,y1,x2,y2])
            return list_
            
        def violet(img):    
            img_thr_violet = cv2.inRange(img,(160,105,170),(220,160,230))
            contours1 = cv2.findContours(img_thr_violet, 
                    cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            list_ = []
            for con in contours1[0]:
                if (cv2.contourArea(con) >300):
                    x,y,w,h = cv2.boundingRect(con)
                    x1,y1,x2,y2 = x,y, x+w ,y+h
                    list_.append([x1,y1,x2,y2])
            return list_
            
        def brown(img):    
            img_thr_brown = cv2.inRange(img,(125,115,105),(200,180,175))
            contours1 = cv2.findContours(img_thr_brown, 
                    cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            list_ = []
            for con in contours1[0]:
                if (cv2.contourArea(con) >300):
                    x,y,w,h = cv2.boundingRect(con)
                    x1,y1,x2,y2 = x,y, x+w ,y+h
                    list_.append([x1,y1,x2,y2])
            return list_
            
        def yellow(img):    
            img_thr_yellow =  cv2.inRange(img,(200,200,100),(255,230,150))&(img[:,:,1]-img[:,:,2]>50)&(img[:,:,0]-img[:,:,2]>75)
            
            contours1 = cv2.findContours(img_thr_yellow, 
                    cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            list_ = []
            for con in contours1[0]:
                if (cv2.contourArea(con) >300):
                    x,y,w,h = cv2.boundingRect(con)
                    x1,y1,x2,y2 = x,y, x+w ,y+h
                    list_.append([x1,y1,x2,y2])
            return list_

        def match(img_1, img_2):
            x = img_1 == img_2 
            return np.count_nonzero(x)/10000    

        def predict(img): 
            list_x_y =    blue(img) + red(img) + brown(img) + violet(img) + green(img) + yellow(img)
            list_ = []
            for x1,y1,x2,y2 in list_x_y:
                x = img[y1:y2,x1:x2]
                
                x = cv2.cvtColor(x,cv2.COLOR_RGB2GRAY)
                x = cv2.resize(x,[100,100])
                otsu_threshold, image_result = cv2.threshold(x, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU,)
                img_thershold = np.uint8(image_result== 0)
                
                list_.append(img_thershold)
            agrmax = {"ti_le" : 0,"index" : [0,1] }
            for i in range(len(list_)) :
                for j in range(i + 1 ,len(list_)):
                    l =  match(list_[i],list_[j])
                    if l > agrmax["ti_le"] :
                        agrmax["ti_le"]  = l 
                        agrmax["index"] = [i,j]
            i1,i2 = agrmax["index"]
            return list_x_y[i1],list_x_y[i2],agrmax["ti_le"]

        img = self.dataset["bigimage"]["image"][:,:,::-1]
        img = img *1
        r1,r2,y = predict(img)
        x1,y1,x2,y2 = r1
        point_1 = (x1+x2)//2, (y1+y2)//2
        x1,y1,x2,y2 = r2     
        point_2 = (x1+x2)//2, (y1+y2)//2

        size1 = (340,212)
        (height, width, channels) = img.shape
        result = scale((width ,height), size1, (point_1, point_2))
        # input(("3d", result))
        return result
