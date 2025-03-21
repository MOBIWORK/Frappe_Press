# Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and Contributors
# For license information, please see license.txt

import frappe
from press.api.account import get_account_request_from_key

DISTRICTS = [
    {
        "name": 'Quận Ba Đình',
        "value": 'Quận Ba Đình',
        "parent": 'Thành phố Hà Nội'
    },
    {
        "name": 'Quận Hoàn Kiếm',
        "value": 'Quận Hoàn Kiếm',
        "parent": 'Thành phố Hà Nội'
    },
    {
        "name": 'Quận Tây Hồ',
        "value": 'Quận Tây Hồ',
        "parent": 'Thành phố Hà Nội'
    },
    {
        "name": 'Quận Long Biên',
        "value": 'Quận Long Biên',
        "parent": 'Thành phố Hà Nội'
    },
    {
        "name": 'Quận Cầu Giấy',
        "value": 'Quận Cầu Giấy',
        "parent": 'Thành phố Hà Nội'
    },
    {
        "name": 'Quận Đống Đa',
        "value": 'Quận Đống Đa',
        "parent": 'Thành phố Hà Nội'
    },
    {
        "name": 'Quận Hai Bà Trưng',
        "value": 'Quận Hai Bà Trưng',
        "parent": 'Thành phố Hà Nội'
    },
    {
        "name": 'Quận Hoàng Mai',
        "value": 'Quận Hoàng Mai',
        "parent": 'Thành phố Hà Nội'
    },
    {
        "name": 'Quận Thanh Xuân',
        "value": 'Quận Thanh Xuân',
        "parent": 'Thành phố Hà Nội'
    },
    {
        "name": 'Huyện Sóc Sơn',
        "value": 'Huyện Sóc Sơn',
        "parent": 'Thành phố Hà Nội'
    },
    {
        "name": 'Huyện Đông Anh',
        "value": 'Huyện Đông Anh',
        "parent": 'Thành phố Hà Nội'
    },
    {
        "name": 'Huyện Gia Lâm',
        "value": 'Huyện Gia Lâm',
        "parent": 'Thành phố Hà Nội'
    },
    {
        "name": 'Quận Nam Từ Liêm',
        "value": 'Quận Nam Từ Liêm',
        "parent": 'Thành phố Hà Nội'
    },
    {
        "name": 'Huyện Thanh Trì',
        "value": 'Huyện Thanh Trì',
        "parent": 'Thành phố Hà Nội'
    },
    {
        "name": 'Quận Bắc Từ Liêm',
        "value": 'Quận Bắc Từ Liêm',
        "parent": 'Thành phố Hà Nội'
    },
    {
        "name": 'Huyện Mê Linh',
        "value": 'Huyện Mê Linh',
        "parent": 'Thành phố Hà Nội'
    },
    {
        "name": 'Quận Hà Đông',
        "value": 'Quận Hà Đông',
        "parent": 'Thành phố Hà Nội'
    },
    {
        "name": 'Thị xã Sơn Tây',
        "value": 'Thị xã Sơn Tây',
        "parent": 'Thành phố Hà Nội'
    },
    {
        "name": 'Huyện Ba Vì',
        "value": 'Huyện Ba Vì',
        "parent": 'Thành phố Hà Nội'
    },
    {
        "name": 'Huyện Phúc Thọ',
        "value": 'Huyện Phúc Thọ',
        "parent": 'Thành phố Hà Nội'
    },
    {
        "name": 'Huyện Đan Phượng',
        "value": 'Huyện Đan Phượng',
        "parent": 'Thành phố Hà Nội'
    },
    {
        "name": 'Huyện Hoài Đức',
        "value": 'Huyện Hoài Đức',
        "parent": 'Thành phố Hà Nội'
    },
    {
        "name": 'Huyện Quốc Oai',
        "value": 'Huyện Quốc Oai',
        "parent": 'Thành phố Hà Nội'
    },
    {
        "name": 'Huyện Thạch Thất',
        "value": 'Huyện Thạch Thất',
        "parent": 'Thành phố Hà Nội'
    },
    {
        "name": 'Huyện Chương Mỹ',
        "value": 'Huyện Chương Mỹ',
        "parent": 'Thành phố Hà Nội'
    },
    {
        "name": 'Huyện Thanh Oai',
        "value": 'Huyện Thanh Oai',
        "parent": 'Thành phố Hà Nội'
    },
    {
        "name": 'Huyện Thường Tín',
        "value": 'Huyện Thường Tín',
        "parent": 'Thành phố Hà Nội'
    },
    {
        "name": 'Huyện Phú Xuyên',
        "value": 'Huyện Phú Xuyên',
        "parent": 'Thành phố Hà Nội'
    },
    {
        "name": 'Huyện Ứng Hòa',
        "value": 'Huyện Ứng Hòa',
        "parent": 'Thành phố Hà Nội'
    },
    {
        "name": 'Huyện Mỹ Đức',
        "value": 'Huyện Mỹ Đức',
        "parent": 'Thành phố Hà Nội'
    },
    {
        "name": 'Thành phố Hà Giang',
        "value": 'Thành phố Hà Giang',
        "parent": 'Tỉnh Hà Giang'
    },
    {
        "name": 'Huyện Đồng Văn',
        "value": 'Huyện Đồng Văn',
        "parent": 'Tỉnh Hà Giang'
    },
    {
        "name": 'Huyện Mèo Vạc',
        "value": 'Huyện Mèo Vạc',
        "parent": 'Tỉnh Hà Giang'
    },
    {
        "name": 'Huyện Yên Minh',
        "value": 'Huyện Yên Minh',
        "parent": 'Tỉnh Hà Giang'
    },
    {
        "name": 'Huyện Quản Bạ',
        "value": 'Huyện Quản Bạ',
        "parent": 'Tỉnh Hà Giang'
    },
    {
        "name": 'Huyện Vị Xuyên',
        "value": 'Huyện Vị Xuyên',
        "parent": 'Tỉnh Hà Giang'
    },
    {
        "name": 'Huyện Bắc Mê',
        "value": 'Huyện Bắc Mê',
        "parent": 'Tỉnh Hà Giang'
    },
    {
        "name": 'Huyện Hoàng Su Phì',
        "value": 'Huyện Hoàng Su Phì',
        "parent": 'Tỉnh Hà Giang'
    },
    {
        "name": 'Huyện Xín Mần',
        "value": 'Huyện Xín Mần',
        "parent": 'Tỉnh Hà Giang'
    },
    {
        "name": 'Huyện Bắc Quang',
        "value": 'Huyện Bắc Quang',
        "parent": 'Tỉnh Hà Giang'
    },
    {
        "name": 'Huyện Quang Bình',
        "value": 'Huyện Quang Bình',
        "parent": 'Tỉnh Hà Giang'
    },
    {
        "name": 'Thành phố Cao Bằng',
        "value": 'Thành phố Cao Bằng',
        "parent": 'Tỉnh Cao Bằng'
    },
    {
        "name": 'Huyện Bảo Lâm',
        "value": 'Huyện Bảo Lâm',
        "parent": 'Tỉnh Cao Bằng'
    },
    {
        "name": 'Huyện Bảo Lạc',
        "value": 'Huyện Bảo Lạc',
        "parent": 'Tỉnh Cao Bằng'
    },
    {
        "name": 'Huyện Hà Quảng',
        "value": 'Huyện Hà Quảng',
        "parent": 'Tỉnh Cao Bằng'
    },
    {
        "name": 'Huyện Trùng Khánh',
        "value": 'Huyện Trùng Khánh',
        "parent": 'Tỉnh Cao Bằng'
    },
    {
        "name": 'Huyện Hạ Lang',
        "value": 'Huyện Hạ Lang',
        "parent": 'Tỉnh Cao Bằng'
    },
    {
        "name": 'Huyện Quảng Hòa',
        "value": 'Huyện Quảng Hòa',
        "parent": 'Tỉnh Cao Bằng'
    },
    {
        "name": 'Huyện Hòa An',
        "value": 'Huyện Hòa An',
        "parent": 'Tỉnh Cao Bằng'
    },
    {
        "name": 'Huyện Nguyên Bình',
        "value": 'Huyện Nguyên Bình',
        "parent": 'Tỉnh Cao Bằng'
    },
    {
        "name": 'Huyện Thạch An',
        "value": 'Huyện Thạch An',
        "parent": 'Tỉnh Cao Bằng'
    },
    {
        "name": 'Thành Phố Bắc Kạn',
        "value": 'Thành Phố Bắc Kạn',
        "parent": 'Tỉnh Bắc Kạn'
    },
    {
        "name": 'Huyện Pác Nặm',
        "value": 'Huyện Pác Nặm',
        "parent": 'Tỉnh Bắc Kạn'
    },
    {
        "name": 'Huyện Ba Bể',
        "value": 'Huyện Ba Bể',
        "parent": 'Tỉnh Bắc Kạn'
    },
    {
        "name": 'Huyện Ngân Sơn',
        "value": 'Huyện Ngân Sơn',
        "parent": 'Tỉnh Bắc Kạn'
    },
    {
        "name": 'Huyện Bạch Thông',
        "value": 'Huyện Bạch Thông',
        "parent": 'Tỉnh Bắc Kạn'
    },
    {
        "name": 'Huyện Chợ Đồn',
        "value": 'Huyện Chợ Đồn',
        "parent": 'Tỉnh Bắc Kạn'
    },
    {
        "name": 'Huyện Chợ Mới',
        "value": 'Huyện Chợ Mới',
        "parent": 'Tỉnh Bắc Kạn'
    },
    {
        "name": 'Huyện Na Rì',
        "value": 'Huyện Na Rì',
        "parent": 'Tỉnh Bắc Kạn'
    },
    {
        "name": 'Thành phố Tuyên Quang',
        "value": 'Thành phố Tuyên Quang',
        "parent": 'Tỉnh Tuyên Quang'
    },
    {
        "name": 'Huyện Lâm Bình',
        "value": 'Huyện Lâm Bình',
        "parent": 'Tỉnh Tuyên Quang'
    },
    {
        "name": 'Huyện Na Hang',
        "value": 'Huyện Na Hang',
        "parent": 'Tỉnh Tuyên Quang'
    },
    {
        "name": 'Huyện Chiêm Hóa',
        "value": 'Huyện Chiêm Hóa',
        "parent": 'Tỉnh Tuyên Quang'
    },
    {
        "name": 'Huyện Hàm Yên',
        "value": 'Huyện Hàm Yên',
        "parent": 'Tỉnh Tuyên Quang'
    },
    {
        "name": 'Huyện Yên Sơn',
        "value": 'Huyện Yên Sơn',
        "parent": 'Tỉnh Tuyên Quang'
    },
    {
        "name": 'Huyện Sơn Dương',
        "value": 'Huyện Sơn Dương',
        "parent": 'Tỉnh Tuyên Quang'
    },
    {
        "name": 'Thành phố Lào Cai',
        "value": 'Thành phố Lào Cai',
        "parent": 'Tỉnh Lào Cai'
    },
    {
        "name": 'Huyện Bát Xát',
        "value": 'Huyện Bát Xát',
        "parent": 'Tỉnh Lào Cai'
    },
    {
        "name": 'Huyện Mường Khương',
        "value": 'Huyện Mường Khương',
        "parent": 'Tỉnh Lào Cai'
    },
    {
        "name": 'Huyện Si Ma Cai',
        "value": 'Huyện Si Ma Cai',
        "parent": 'Tỉnh Lào Cai'
    },
    {
        "name": 'Huyện Bắc Hà',
        "value": 'Huyện Bắc Hà',
        "parent": 'Tỉnh Lào Cai'
    },
    {
        "name": 'Huyện Bảo Thắng',
        "value": 'Huyện Bảo Thắng',
        "parent": 'Tỉnh Lào Cai'
    },
    {
        "name": 'Huyện Bảo Yên',
        "value": 'Huyện Bảo Yên',
        "parent": 'Tỉnh Lào Cai'
    },
    {
        "name": 'Thị xã Sa Pa',
        "value": 'Thị xã Sa Pa',
        "parent": 'Tỉnh Lào Cai'
    },
    {
        "name": 'Huyện Văn Bàn',
        "value": 'Huyện Văn Bàn',
        "parent": 'Tỉnh Lào Cai'
    },
    {
        "name": 'Thành phố Điện Biên Phủ',
        "value": 'Thành phố Điện Biên Phủ',
        "parent": 'Tỉnh Điện Biên'
    },
    {
        "name": 'Thị Xã Mường Lay',
        "value": 'Thị Xã Mường Lay',
        "parent": 'Tỉnh Điện Biên'
    },
    {
        "name": 'Huyện Mường Nhé',
        "value": 'Huyện Mường Nhé',
        "parent": 'Tỉnh Điện Biên'
    },
    {
        "name": 'Huyện Mường Chà',
        "value": 'Huyện Mường Chà',
        "parent": 'Tỉnh Điện Biên'
    },
    {
        "name": 'Huyện Tủa Chùa',
        "value": 'Huyện Tủa Chùa',
        "parent": 'Tỉnh Điện Biên'
    },
    {
        "name": 'Huyện Tuần Giáo',
        "value": 'Huyện Tuần Giáo',
        "parent": 'Tỉnh Điện Biên'
    },
    {
        "name": 'Huyện Điện Biên',
        "value": 'Huyện Điện Biên',
        "parent": 'Tỉnh Điện Biên'
    },
    {
        "name": 'Huyện Điện Biên Đông',
        "value": 'Huyện Điện Biên Đông',
        "parent": 'Tỉnh Điện Biên'
    },
    {
        "name": 'Huyện Mường Ảng',
        "value": 'Huyện Mường Ảng',
        "parent": 'Tỉnh Điện Biên'
    },
    {
        "name": 'Huyện Nậm Pồ',
        "value": 'Huyện Nậm Pồ',
        "parent": 'Tỉnh Điện Biên'
    },
    {
        "name": 'Thành phố Lai Châu',
        "value": 'Thành phố Lai Châu',
        "parent": 'Tỉnh Lai Châu'
    },
    {
        "name": 'Huyện Tam Đường',
        "value": 'Huyện Tam Đường',
        "parent": 'Tỉnh Lai Châu'
    },
    {
        "name": 'Huyện Mường Tè',
        "value": 'Huyện Mường Tè',
        "parent": 'Tỉnh Lai Châu'
    },
    {
        "name": 'Huyện Sìn Hồ',
        "value": 'Huyện Sìn Hồ',
        "parent": 'Tỉnh Lai Châu'
    },
    {
        "name": 'Huyện Phong Thổ',
        "value": 'Huyện Phong Thổ',
        "parent": 'Tỉnh Lai Châu'
    },
    {
        "name": 'Huyện Than Uyên',
        "value": 'Huyện Than Uyên',
        "parent": 'Tỉnh Lai Châu'
    },
    {
        "name": 'Huyện Tân Uyên',
        "value": 'Huyện Tân Uyên',
        "parent": 'Tỉnh Lai Châu'
    },
    {
        "name": 'Huyện Nậm Nhùn',
        "value": 'Huyện Nậm Nhùn',
        "parent": 'Tỉnh Lai Châu'
    },
    {
        "name": 'Thành phố Sơn La',
        "value": 'Thành phố Sơn La',
        "parent": 'Tỉnh Sơn La'
    },
    {
        "name": 'Huyện Quỳnh Nhai',
        "value": 'Huyện Quỳnh Nhai',
        "parent": 'Tỉnh Sơn La'
    },
    {
        "name": 'Huyện Thuận Châu',
        "value": 'Huyện Thuận Châu',
        "parent": 'Tỉnh Sơn La'
    },
    {
        "name": 'Huyện Mường La',
        "value": 'Huyện Mường La',
        "parent": 'Tỉnh Sơn La'
    },
    {
        "name": 'Huyện Bắc Yên',
        "value": 'Huyện Bắc Yên',
        "parent": 'Tỉnh Sơn La'
    },
    {
        "name": 'Huyện Phù Yên',
        "value": 'Huyện Phù Yên',
        "parent": 'Tỉnh Sơn La'
    },
    {
        "name": 'Huyện Mộc Châu',
        "value": 'Huyện Mộc Châu',
        "parent": 'Tỉnh Sơn La'
    },
    {
        "name": 'Huyện Yên Châu',
        "value": 'Huyện Yên Châu',
        "parent": 'Tỉnh Sơn La'
    },
    {
        "name": 'Huyện Mai Sơn',
        "value": 'Huyện Mai Sơn',
        "parent": 'Tỉnh Sơn La'
    },
    {
        "name": 'Huyện Sông Mã',
        "value": 'Huyện Sông Mã',
        "parent": 'Tỉnh Sơn La'
    },
    {
        "name": 'Huyện Sốp Cộp',
        "value": 'Huyện Sốp Cộp',
        "parent": 'Tỉnh Sơn La'
    },
    {
        "name": 'Huyện Vân Hồ',
        "value": 'Huyện Vân Hồ',
        "parent": 'Tỉnh Sơn La'
    },
    {
        "name": 'Thành phố Yên Bái',
        "value": 'Thành phố Yên Bái',
        "parent": 'Tỉnh Yên Bái'
    },
    {
        "name": 'Thị xã Nghĩa Lộ',
        "value": 'Thị xã Nghĩa Lộ',
        "parent": 'Tỉnh Yên Bái'
    },
    {
        "name": 'Huyện Lục Yên',
        "value": 'Huyện Lục Yên',
        "parent": 'Tỉnh Yên Bái'
    },
    {
        "name": 'Huyện Văn Yên',
        "value": 'Huyện Văn Yên',
        "parent": 'Tỉnh Yên Bái'
    },
    {
        "name": 'Huyện Mù Căng Chải',
        "value": 'Huyện Mù Căng Chải',
        "parent": 'Tỉnh Yên Bái'
    },
    {
        "name": 'Huyện Trấn Yên',
        "value": 'Huyện Trấn Yên',
        "parent": 'Tỉnh Yên Bái'
    },
    {
        "name": 'Huyện Trạm Tấu',
        "value": 'Huyện Trạm Tấu',
        "parent": 'Tỉnh Yên Bái'
    },
    {
        "name": 'Huyện Văn Chấn',
        "value": 'Huyện Văn Chấn',
        "parent": 'Tỉnh Yên Bái'
    },
    {
        "name": 'Huyện Yên Bình',
        "value": 'Huyện Yên Bình',
        "parent": 'Tỉnh Yên Bái'
    },
    {
        "name": 'Thành phố Hòa Bình',
        "value": 'Thành phố Hòa Bình',
        "parent": 'Tỉnh Hòa Bình'
    },
    {
        "name": 'Huyện Đà Bắc',
        "value": 'Huyện Đà Bắc',
        "parent": 'Tỉnh Hòa Bình'
    },
    {
        "name": 'Huyện Lương Sơn',
        "value": 'Huyện Lương Sơn',
        "parent": 'Tỉnh Hòa Bình'
    },
    {
        "name": 'Huyện Kim Bôi',
        "value": 'Huyện Kim Bôi',
        "parent": 'Tỉnh Hòa Bình'
    },
    {
        "name": 'Huyện Cao Phong',
        "value": 'Huyện Cao Phong',
        "parent": 'Tỉnh Hòa Bình'
    },
    {
        "name": 'Huyện Tân Lạc',
        "value": 'Huyện Tân Lạc',
        "parent": 'Tỉnh Hòa Bình'
    },
    {
        "name": 'Huyện Mai Châu',
        "value": 'Huyện Mai Châu',
        "parent": 'Tỉnh Hòa Bình'
    },
    {
        "name": 'Huyện Lạc Sơn',
        "value": 'Huyện Lạc Sơn',
        "parent": 'Tỉnh Hòa Bình'
    },
    {
        "name": 'Huyện Yên Thủy',
        "value": 'Huyện Yên Thủy',
        "parent": 'Tỉnh Hòa Bình'
    },
    {
        "name": 'Huyện Lạc Thủy',
        "value": 'Huyện Lạc Thủy',
        "parent": 'Tỉnh Hòa Bình'
    },
    {
        "name": 'Thành phố Thái Nguyên',
        "value": 'Thành phố Thái Nguyên',
        "parent": 'Tỉnh Thái Nguyên'
    },
    {
        "name": 'Thành phố Sông Công',
        "value": 'Thành phố Sông Công',
        "parent": 'Tỉnh Thái Nguyên'
    },
    {
        "name": 'Huyện Định Hóa',
        "value": 'Huyện Định Hóa',
        "parent": 'Tỉnh Thái Nguyên'
    },
    {
        "name": 'Huyện Phú Lương',
        "value": 'Huyện Phú Lương',
        "parent": 'Tỉnh Thái Nguyên'
    },
    {
        "name": 'Huyện Đồng Hỷ',
        "value": 'Huyện Đồng Hỷ',
        "parent": 'Tỉnh Thái Nguyên'
    },
    {
        "name": 'Huyện Võ Nhai',
        "value": 'Huyện Võ Nhai',
        "parent": 'Tỉnh Thái Nguyên'
    },
    {
        "name": 'Huyện Đại Từ',
        "value": 'Huyện Đại Từ',
        "parent": 'Tỉnh Thái Nguyên'
    },
    {
        "name": 'Thị xã Phổ Yên',
        "value": 'Thị xã Phổ Yên',
        "parent": 'Tỉnh Thái Nguyên'
    },
    {
        "name": 'Huyện Phú Bình',
        "value": 'Huyện Phú Bình',
        "parent": 'Tỉnh Thái Nguyên'
    },
    {
        "name": 'Thành phố Lạng Sơn',
        "value": 'Thành phố Lạng Sơn',
        "parent": 'Tỉnh Lạng Sơn'
    },
    {
        "name": 'Huyện Tràng Định',
        "value": 'Huyện Tràng Định',
        "parent": 'Tỉnh Lạng Sơn'
    },
    {
        "name": 'Huyện Bình Gia',
        "value": 'Huyện Bình Gia',
        "parent": 'Tỉnh Lạng Sơn'
    },
    {
        "name": 'Huyện Văn Lãng',
        "value": 'Huyện Văn Lãng',
        "parent": 'Tỉnh Lạng Sơn'
    },
    {
        "name": 'Huyện Cao Lộc',
        "value": 'Huyện Cao Lộc',
        "parent": 'Tỉnh Lạng Sơn'
    },
    {
        "name": 'Huyện Văn Quan',
        "value": 'Huyện Văn Quan',
        "parent": 'Tỉnh Lạng Sơn'
    },
    {
        "name": 'Huyện Bắc Sơn',
        "value": 'Huyện Bắc Sơn',
        "parent": 'Tỉnh Lạng Sơn'
    },
    {
        "name": 'Huyện Hữu Lũng',
        "value": 'Huyện Hữu Lũng',
        "parent": 'Tỉnh Lạng Sơn'
    },
    {
        "name": 'Huyện Chi Lăng',
        "value": 'Huyện Chi Lăng',
        "parent": 'Tỉnh Lạng Sơn'
    },
    {
        "name": 'Huyện Lộc Bình',
        "value": 'Huyện Lộc Bình',
        "parent": 'Tỉnh Lạng Sơn'
    },
    {
        "name": 'Huyện Đình Lập',
        "value": 'Huyện Đình Lập',
        "parent": 'Tỉnh Lạng Sơn'
    },
    {
        "name": 'Thành phố Hạ Long',
        "value": 'Thành phố Hạ Long',
        "parent": 'Tỉnh Quảng Ninh'
    },
    {
        "name": 'Thành phố Móng Cái',
        "value": 'Thành phố Móng Cái',
        "parent": 'Tỉnh Quảng Ninh'
    },
    {
        "name": 'Thành phố Cẩm Phả',
        "value": 'Thành phố Cẩm Phả',
        "parent": 'Tỉnh Quảng Ninh'
    },
    {
        "name": 'Thành phố Uông Bí',
        "value": 'Thành phố Uông Bí',
        "parent": 'Tỉnh Quảng Ninh'
    },
    {
        "name": 'Huyện Bình Liêu',
        "value": 'Huyện Bình Liêu',
        "parent": 'Tỉnh Quảng Ninh'
    },
    {
        "name": 'Huyện Tiên Yên',
        "value": 'Huyện Tiên Yên',
        "parent": 'Tỉnh Quảng Ninh'
    },
    {
        "name": 'Huyện Đầm Hà',
        "value": 'Huyện Đầm Hà',
        "parent": 'Tỉnh Quảng Ninh'
    },
    {
        "name": 'Huyện Hải Hà',
        "value": 'Huyện Hải Hà',
        "parent": 'Tỉnh Quảng Ninh'
    },
    {
        "name": 'Huyện Ba Chẽ',
        "value": 'Huyện Ba Chẽ',
        "parent": 'Tỉnh Quảng Ninh'
    },
    {
        "name": 'Huyện Vân Đồn',
        "value": 'Huyện Vân Đồn',
        "parent": 'Tỉnh Quảng Ninh'
    },
    {
        "name": 'Thị xã Đông Triều',
        "value": 'Thị xã Đông Triều',
        "parent": 'Tỉnh Quảng Ninh'
    },
    {
        "name": 'Thị xã Quảng Yên',
        "value": 'Thị xã Quảng Yên',
        "parent": 'Tỉnh Quảng Ninh'
    },
    {
        "name": 'Huyện Cô Tô',
        "value": 'Huyện Cô Tô',
        "parent": 'Tỉnh Quảng Ninh'
    },
    {
        "name": 'Thành phố Bắc Giang',
        "value": 'Thành phố Bắc Giang',
        "parent": 'Tỉnh Bắc Giang'
    },
    {
        "name": 'Huyện Yên Thế',
        "value": 'Huyện Yên Thế',
        "parent": 'Tỉnh Bắc Giang'
    },
    {
        "name": 'Huyện Tân Yên',
        "value": 'Huyện Tân Yên',
        "parent": 'Tỉnh Bắc Giang'
    },
    {
        "name": 'Huyện Lạng Giang',
        "value": 'Huyện Lạng Giang',
        "parent": 'Tỉnh Bắc Giang'
    },
    {
        "name": 'Huyện Lục Nam',
        "value": 'Huyện Lục Nam',
        "parent": 'Tỉnh Bắc Giang'
    },
    {
        "name": 'Huyện Lục Ngạn',
        "value": 'Huyện Lục Ngạn',
        "parent": 'Tỉnh Bắc Giang'
    },
    {
        "name": 'Huyện Sơn Động',
        "value": 'Huyện Sơn Động',
        "parent": 'Tỉnh Bắc Giang'
    },
    {
        "name": 'Huyện Yên Dũng',
        "value": 'Huyện Yên Dũng',
        "parent": 'Tỉnh Bắc Giang'
    },
    {
        "name": 'Huyện Việt Yên',
        "value": 'Huyện Việt Yên',
        "parent": 'Tỉnh Bắc Giang'
    },
    {
        "name": 'Huyện Hiệp Hòa',
        "value": 'Huyện Hiệp Hòa',
        "parent": 'Tỉnh Bắc Giang'
    },
    {
        "name": 'Thành phố Việt Trì',
        "value": 'Thành phố Việt Trì',
        "parent": 'Tỉnh Phú Thọ'
    },
    {
        "name": 'Thị xã Phú Thọ',
        "value": 'Thị xã Phú Thọ',
        "parent": 'Tỉnh Phú Thọ'
    },
    {
        "name": 'Huyện Đoan Hùng',
        "value": 'Huyện Đoan Hùng',
        "parent": 'Tỉnh Phú Thọ'
    },
    {
        "name": 'Huyện Hạ Hòa',
        "value": 'Huyện Hạ Hòa',
        "parent": 'Tỉnh Phú Thọ'
    },
    {
        "name": 'Huyện Thanh Ba',
        "value": 'Huyện Thanh Ba',
        "parent": 'Tỉnh Phú Thọ'
    },
    {
        "name": 'Huyện Phù Ninh',
        "value": 'Huyện Phù Ninh',
        "parent": 'Tỉnh Phú Thọ'
    },
    {
        "name": 'Huyện Yên Lập',
        "value": 'Huyện Yên Lập',
        "parent": 'Tỉnh Phú Thọ'
    },
    {
        "name": 'Huyện Cẩm Khê',
        "value": 'Huyện Cẩm Khê',
        "parent": 'Tỉnh Phú Thọ'
    },
    {
        "name": 'Huyện Tam Nông',
        "value": 'Huyện Tam Nông',
        "parent": 'Tỉnh Phú Thọ'
    },
    {
        "name": 'Huyện Lâm Thao',
        "value": 'Huyện Lâm Thao',
        "parent": 'Tỉnh Phú Thọ'
    },
    {
        "name": 'Huyện Thanh Sơn',
        "value": 'Huyện Thanh Sơn',
        "parent": 'Tỉnh Phú Thọ'
    },
    {
        "name": 'Huyện Thanh Thủy',
        "value": 'Huyện Thanh Thủy',
        "parent": 'Tỉnh Phú Thọ'
    },
    {
        "name": 'Huyện Tân Sơn',
        "value": 'Huyện Tân Sơn',
        "parent": 'Tỉnh Phú Thọ'
    },
    {
        "name": 'Thành phố Vĩnh Yên',
        "value": 'Thành phố Vĩnh Yên',
        "parent": 'Tỉnh Vĩnh Phúc'
    },
    {
        "name": 'Thành phố Phúc Yên',
        "value": 'Thành phố Phúc Yên',
        "parent": 'Tỉnh Vĩnh Phúc'
    },
    {
        "name": 'Huyện Lập Thạch',
        "value": 'Huyện Lập Thạch',
        "parent": 'Tỉnh Vĩnh Phúc'
    },
    {
        "name": 'Huyện Tam Dương',
        "value": 'Huyện Tam Dương',
        "parent": 'Tỉnh Vĩnh Phúc'
    },
    {
        "name": 'Huyện Tam Đảo',
        "value": 'Huyện Tam Đảo',
        "parent": 'Tỉnh Vĩnh Phúc'
    },
    {
        "name": 'Huyện Bình Xuyên',
        "value": 'Huyện Bình Xuyên',
        "parent": 'Tỉnh Vĩnh Phúc'
    },
    {
        "name": 'Huyện Yên Lạc',
        "value": 'Huyện Yên Lạc',
        "parent": 'Tỉnh Vĩnh Phúc'
    },
    {
        "name": 'Huyện Vĩnh Tường',
        "value": 'Huyện Vĩnh Tường',
        "parent": 'Tỉnh Vĩnh Phúc'
    },
    {
        "name": 'Huyện Sông Lô',
        "value": 'Huyện Sông Lô',
        "parent": 'Tỉnh Vĩnh Phúc'
    },
    {
        "name": 'Thành phố Bắc Ninh',
        "value": 'Thành phố Bắc Ninh',
        "parent": 'Tỉnh Bắc Ninh'
    },
    {
        "name": 'Huyện Yên Phong',
        "value": 'Huyện Yên Phong',
        "parent": 'Tỉnh Bắc Ninh'
    },
    {
        "name": 'Huyện Quế Võ',
        "value": 'Huyện Quế Võ',
        "parent": 'Tỉnh Bắc Ninh'
    },
    {
        "name": 'Huyện Tiên Du',
        "value": 'Huyện Tiên Du',
        "parent": 'Tỉnh Bắc Ninh'
    },
    {
        "name": 'Thị xã Từ Sơn',
        "value": 'Thị xã Từ Sơn',
        "parent": 'Tỉnh Bắc Ninh'
    },
    {
        "name": 'Huyện Thuận Thành',
        "value": 'Huyện Thuận Thành',
        "parent": 'Tỉnh Bắc Ninh'
    },
    {
        "name": 'Huyện Gia Bình',
        "value": 'Huyện Gia Bình',
        "parent": 'Tỉnh Bắc Ninh'
    },
    {
        "name": 'Huyện Lương Tài',
        "value": 'Huyện Lương Tài',
        "parent": 'Tỉnh Bắc Ninh'
    },
    {
        "name": 'Thành phố Hải Dương',
        "value": 'Thành phố Hải Dương',
        "parent": 'Tỉnh Hải Dương'
    },
    {
        "name": 'Thành phố Chí Linh',
        "value": 'Thành phố Chí Linh',
        "parent": 'Tỉnh Hải Dương'
    },
    {
        "name": 'Huyện Nam Sách',
        "value": 'Huyện Nam Sách',
        "parent": 'Tỉnh Hải Dương'
    },
    {
        "name": 'Thị xã Kinh Môn',
        "value": 'Thị xã Kinh Môn',
        "parent": 'Tỉnh Hải Dương'
    },
    {
        "name": 'Huyện Kim Thành',
        "value": 'Huyện Kim Thành',
        "parent": 'Tỉnh Hải Dương'
    },
    {
        "name": 'Huyện Thanh Hà',
        "value": 'Huyện Thanh Hà',
        "parent": 'Tỉnh Hải Dương'
    },
    {
        "name": 'Huyện Cẩm Giàng',
        "value": 'Huyện Cẩm Giàng',
        "parent": 'Tỉnh Hải Dương'
    },
    {
        "name": 'Huyện Bình Giang',
        "value": 'Huyện Bình Giang',
        "parent": 'Tỉnh Hải Dương'
    },
    {
        "name": 'Huyện Gia Lộc',
        "value": 'Huyện Gia Lộc',
        "parent": 'Tỉnh Hải Dương'
    },
    {
        "name": 'Huyện Tứ Kỳ',
        "value": 'Huyện Tứ Kỳ',
        "parent": 'Tỉnh Hải Dương'
    },
    {
        "name": 'Huyện Ninh Giang',
        "value": 'Huyện Ninh Giang',
        "parent": 'Tỉnh Hải Dương'
    },
    {
        "name": 'Huyện Thanh Miện',
        "value": 'Huyện Thanh Miện',
        "parent": 'Tỉnh Hải Dương'
    },
    {
        "name": 'Quận Hồng Bàng',
        "value": 'Quận Hồng Bàng',
        "parent": 'Thành phố Hải Phòng'
    },
    {
        "name": 'Quận Ngô Quyền',
        "value": 'Quận Ngô Quyền',
        "parent": 'Thành phố Hải Phòng'
    },
    {
        "name": 'Quận Lê Chân',
        "value": 'Quận Lê Chân',
        "parent": 'Thành phố Hải Phòng'
    },
    {
        "name": 'Quận Hải An',
        "value": 'Quận Hải An',
        "parent": 'Thành phố Hải Phòng'
    },
    {
        "name": 'Quận Kiến An',
        "value": 'Quận Kiến An',
        "parent": 'Thành phố Hải Phòng'
    },
    {
        "name": 'Quận Đồ Sơn',
        "value": 'Quận Đồ Sơn',
        "parent": 'Thành phố Hải Phòng'
    },
    {
        "name": 'Quận Dương Kinh',
        "value": 'Quận Dương Kinh',
        "parent": 'Thành phố Hải Phòng'
    },
    {
        "name": 'Huyện Thủy Nguyên',
        "value": 'Huyện Thủy Nguyên',
        "parent": 'Thành phố Hải Phòng'
    },
    {
        "name": 'Huyện An Dương',
        "value": 'Huyện An Dương',
        "parent": 'Thành phố Hải Phòng'
    },
    {
        "name": 'Huyện An Lão',
        "value": 'Huyện An Lão',
        "parent": 'Thành phố Hải Phòng'
    },
    {
        "name": 'Huyện Kiến Thụy',
        "value": 'Huyện Kiến Thụy',
        "parent": 'Thành phố Hải Phòng'
    },
    {
        "name": 'Huyện Tiên Lãng',
        "value": 'Huyện Tiên Lãng',
        "parent": 'Thành phố Hải Phòng'
    },
    {
        "name": 'Huyện Vĩnh Bảo',
        "value": 'Huyện Vĩnh Bảo',
        "parent": 'Thành phố Hải Phòng'
    },
    {
        "name": 'Huyện Cát Hải',
        "value": 'Huyện Cát Hải',
        "parent": 'Thành phố Hải Phòng'
    },
    {
        "name": 'Huyện Bạch Long Vĩ',
        "value": 'Huyện Bạch Long Vĩ',
        "parent": 'Thành phố Hải Phòng'
    },
    {
        "name": 'Thành phố Hưng Yên',
        "value": 'Thành phố Hưng Yên',
        "parent": 'Tỉnh Hưng Yên'
    },
    {
        "name": 'Huyện Văn Lâm',
        "value": 'Huyện Văn Lâm',
        "parent": 'Tỉnh Hưng Yên'
    },
    {
        "name": 'Huyện Văn Giang',
        "value": 'Huyện Văn Giang',
        "parent": 'Tỉnh Hưng Yên'
    },
    {
        "name": 'Huyện Yên Mỹ',
        "value": 'Huyện Yên Mỹ',
        "parent": 'Tỉnh Hưng Yên'
    },
    {
        "name": 'Thị xã Mỹ Hào',
        "value": 'Thị xã Mỹ Hào',
        "parent": 'Tỉnh Hưng Yên'
    },
    {
        "name": 'Huyện Ân Thi',
        "value": 'Huyện Ân Thi',
        "parent": 'Tỉnh Hưng Yên'
    },
    {
        "name": 'Huyện Khoái Châu',
        "value": 'Huyện Khoái Châu',
        "parent": 'Tỉnh Hưng Yên'
    },
    {
        "name": 'Huyện Kim Động',
        "value": 'Huyện Kim Động',
        "parent": 'Tỉnh Hưng Yên'
    },
    {
        "name": 'Huyện Tiên Lữ',
        "value": 'Huyện Tiên Lữ',
        "parent": 'Tỉnh Hưng Yên'
    },
    {
        "name": 'Huyện Phù Cừ',
        "value": 'Huyện Phù Cừ',
        "parent": 'Tỉnh Hưng Yên'
    },
    {
        "name": 'Thành phố Thái Bình',
        "value": 'Thành phố Thái Bình',
        "parent": 'Tỉnh Thái Bình'
    },
    {
        "name": 'Huyện Quỳnh Phụ',
        "value": 'Huyện Quỳnh Phụ',
        "parent": 'Tỉnh Thái Bình'
    },
    {
        "name": 'Huyện Hưng Hà',
        "value": 'Huyện Hưng Hà',
        "parent": 'Tỉnh Thái Bình'
    },
    {
        "name": 'Huyện Đông Hưng',
        "value": 'Huyện Đông Hưng',
        "parent": 'Tỉnh Thái Bình'
    },
    {
        "name": 'Huyện Thái Thụy',
        "value": 'Huyện Thái Thụy',
        "parent": 'Tỉnh Thái Bình'
    },
    {
        "name": 'Huyện Tiền Hải',
        "value": 'Huyện Tiền Hải',
        "parent": 'Tỉnh Thái Bình'
    },
    {
        "name": 'Huyện Kiến Xương',
        "value": 'Huyện Kiến Xương',
        "parent": 'Tỉnh Thái Bình'
    },
    {
        "name": 'Huyện Vũ Thư',
        "value": 'Huyện Vũ Thư',
        "parent": 'Tỉnh Thái Bình'
    },
    {
        "name": 'Thành phố Phủ Lý',
        "value": 'Thành phố Phủ Lý',
        "parent": 'Tỉnh Hà Nam'
    },
    {
        "name": 'Thị xã Duy Tiên',
        "value": 'Thị xã Duy Tiên',
        "parent": 'Tỉnh Hà Nam'
    },
    {
        "name": 'Huyện Kim Bảng',
        "value": 'Huyện Kim Bảng',
        "parent": 'Tỉnh Hà Nam'
    },
    {
        "name": 'Huyện Thanh Liêm',
        "value": 'Huyện Thanh Liêm',
        "parent": 'Tỉnh Hà Nam'
    },
    {
        "name": 'Huyện Bình Lục',
        "value": 'Huyện Bình Lục',
        "parent": 'Tỉnh Hà Nam'
    },
    {
        "name": 'Huyện Lý Nhân',
        "value": 'Huyện Lý Nhân',
        "parent": 'Tỉnh Hà Nam'
    },
    {
        "name": 'Thành phố Nam Định',
        "value": 'Thành phố Nam Định',
        "parent": 'Tỉnh Nam Định'
    },
    {
        "name": 'Huyện Mỹ Lộc',
        "value": 'Huyện Mỹ Lộc',
        "parent": 'Tỉnh Nam Định'
    },
    {
        "name": 'Huyện Vụ Bản',
        "value": 'Huyện Vụ Bản',
        "parent": 'Tỉnh Nam Định'
    },
    {
        "name": 'Huyện Ý Yên',
        "value": 'Huyện Ý Yên',
        "parent": 'Tỉnh Nam Định'
    },
    {
        "name": 'Huyện Nghĩa Hưng',
        "value": 'Huyện Nghĩa Hưng',
        "parent": 'Tỉnh Nam Định'
    },
    {
        "name": 'Huyện Nam Trực',
        "value": 'Huyện Nam Trực',
        "parent": 'Tỉnh Nam Định'
    },
    {
        "name": 'Huyện Trực Ninh',
        "value": 'Huyện Trực Ninh',
        "parent": 'Tỉnh Nam Định'
    },
    {
        "name": 'Huyện Xuân Trường',
        "value": 'Huyện Xuân Trường',
        "parent": 'Tỉnh Nam Định'
    },
    {
        "name": 'Huyện Giao Thủy',
        "value": 'Huyện Giao Thủy',
        "parent": 'Tỉnh Nam Định'
    },
    {
        "name": 'Huyện Hải Hậu',
        "value": 'Huyện Hải Hậu',
        "parent": 'Tỉnh Nam Định'
    },
    {
        "name": 'Thành phố Ninh Bình',
        "value": 'Thành phố Ninh Bình',
        "parent": 'Tỉnh Ninh Bình'
    },
    {
        "name": 'Thành phố Tam Điệp',
        "value": 'Thành phố Tam Điệp',
        "parent": 'Tỉnh Ninh Bình'
    },
    {
        "name": 'Huyện Nho Quan',
        "value": 'Huyện Nho Quan',
        "parent": 'Tỉnh Ninh Bình'
    },
    {
        "name": 'Huyện Gia Viễn',
        "value": 'Huyện Gia Viễn',
        "parent": 'Tỉnh Ninh Bình'
    },
    {
        "name": 'Huyện Hoa Lư',
        "value": 'Huyện Hoa Lư',
        "parent": 'Tỉnh Ninh Bình'
    },
    {
        "name": 'Huyện Yên Khánh',
        "value": 'Huyện Yên Khánh',
        "parent": 'Tỉnh Ninh Bình'
    },
    {
        "name": 'Huyện Kim Sơn',
        "value": 'Huyện Kim Sơn',
        "parent": 'Tỉnh Ninh Bình'
    },
    {
        "name": 'Huyện Yên Mô',
        "value": 'Huyện Yên Mô',
        "parent": 'Tỉnh Ninh Bình'
    },
    {
        "name": 'Thành phố Thanh Hóa',
        "value": 'Thành phố Thanh Hóa',
        "parent": 'Tỉnh Thanh Hóa'
    },
    {
        "name": 'Thị xã Bỉm Sơn',
        "value": 'Thị xã Bỉm Sơn',
        "parent": 'Tỉnh Thanh Hóa'
    },
    {
        "name": 'Thành phố Sầm Sơn',
        "value": 'Thành phố Sầm Sơn',
        "parent": 'Tỉnh Thanh Hóa'
    },
    {
        "name": 'Huyện Mường Lát',
        "value": 'Huyện Mường Lát',
        "parent": 'Tỉnh Thanh Hóa'
    },
    {
        "name": 'Huyện Quan Hóa',
        "value": 'Huyện Quan Hóa',
        "parent": 'Tỉnh Thanh Hóa'
    },
    {
        "name": 'Huyện Bá Thước',
        "value": 'Huyện Bá Thước',
        "parent": 'Tỉnh Thanh Hóa'
    },
    {
        "name": 'Huyện Quan Sơn',
        "value": 'Huyện Quan Sơn',
        "parent": 'Tỉnh Thanh Hóa'
    },
    {
        "name": 'Huyện Lang Chánh',
        "value": 'Huyện Lang Chánh',
        "parent": 'Tỉnh Thanh Hóa'
    },
    {
        "name": 'Huyện Ngọc Lặc',
        "value": 'Huyện Ngọc Lặc',
        "parent": 'Tỉnh Thanh Hóa'
    },
    {
        "name": 'Huyện Cẩm Thủy',
        "value": 'Huyện Cẩm Thủy',
        "parent": 'Tỉnh Thanh Hóa'
    },
    {
        "name": 'Huyện Thạch Thành',
        "value": 'Huyện Thạch Thành',
        "parent": 'Tỉnh Thanh Hóa'
    },
    {
        "name": 'Huyện Hà Trung',
        "value": 'Huyện Hà Trung',
        "parent": 'Tỉnh Thanh Hóa'
    },
    {
        "name": 'Huyện Vĩnh Lộc',
        "value": 'Huyện Vĩnh Lộc',
        "parent": 'Tỉnh Thanh Hóa'
    },
    {
        "name": 'Huyện Yên Định',
        "value": 'Huyện Yên Định',
        "parent": 'Tỉnh Thanh Hóa'
    },
    {
        "name": 'Huyện Thọ Xuân',
        "value": 'Huyện Thọ Xuân',
        "parent": 'Tỉnh Thanh Hóa'
    },
    {
        "name": 'Huyện Thường Xuân',
        "value": 'Huyện Thường Xuân',
        "parent": 'Tỉnh Thanh Hóa'
    },
    {
        "name": 'Huyện Triệu Sơn',
        "value": 'Huyện Triệu Sơn',
        "parent": 'Tỉnh Thanh Hóa'
    },
    {
        "name": 'Huyện Thiệu Hóa',
        "value": 'Huyện Thiệu Hóa',
        "parent": 'Tỉnh Thanh Hóa'
    },
    {
        "name": 'Huyện Hoằng Hóa',
        "value": 'Huyện Hoằng Hóa',
        "parent": 'Tỉnh Thanh Hóa'
    },
    {
        "name": 'Huyện Hậu Lộc',
        "value": 'Huyện Hậu Lộc',
        "parent": 'Tỉnh Thanh Hóa'
    },
    {
        "name": 'Huyện Nga Sơn',
        "value": 'Huyện Nga Sơn',
        "parent": 'Tỉnh Thanh Hóa'
    },
    {
        "name": 'Huyện Như Xuân',
        "value": 'Huyện Như Xuân',
        "parent": 'Tỉnh Thanh Hóa'
    },
    {
        "name": 'Huyện Như Thanh',
        "value": 'Huyện Như Thanh',
        "parent": 'Tỉnh Thanh Hóa'
    },
    {
        "name": 'Huyện Nông Cống',
        "value": 'Huyện Nông Cống',
        "parent": 'Tỉnh Thanh Hóa'
    },
    {
        "name": 'Huyện Đông Sơn',
        "value": 'Huyện Đông Sơn',
        "parent": 'Tỉnh Thanh Hóa'
    },
    {
        "name": 'Huyện Quảng Xương',
        "value": 'Huyện Quảng Xương',
        "parent": 'Tỉnh Thanh Hóa'
    },
    {
        "name": 'Thị xã Nghi Sơn',
        "value": 'Thị xã Nghi Sơn',
        "parent": 'Tỉnh Thanh Hóa'
    },
    {
        "name": 'Thành phố Vinh',
        "value": 'Thành phố Vinh',
        "parent": 'Tỉnh Nghệ An'
    },
    {
        "name": 'Thị xã Cửa Lò',
        "value": 'Thị xã Cửa Lò',
        "parent": 'Tỉnh Nghệ An'
    },
    {
        "name": 'Thị xã Thái Hòa',
        "value": 'Thị xã Thái Hòa',
        "parent": 'Tỉnh Nghệ An'
    },
    {
        "name": 'Huyện Quế Phong',
        "value": 'Huyện Quế Phong',
        "parent": 'Tỉnh Nghệ An'
    },
    {
        "name": 'Huyện Quỳ Châu',
        "value": 'Huyện Quỳ Châu',
        "parent": 'Tỉnh Nghệ An'
    },
    {
        "name": 'Huyện Kỳ Sơn',
        "value": 'Huyện Kỳ Sơn',
        "parent": 'Tỉnh Nghệ An'
    },
    {
        "name": 'Huyện Tương Dương',
        "value": 'Huyện Tương Dương',
        "parent": 'Tỉnh Nghệ An'
    },
    {
        "name": 'Huyện Nghĩa Đàn',
        "value": 'Huyện Nghĩa Đàn',
        "parent": 'Tỉnh Nghệ An'
    },
    {
        "name": 'Huyện Quỳ Hợp',
        "value": 'Huyện Quỳ Hợp',
        "parent": 'Tỉnh Nghệ An'
    },
    {
        "name": 'Huyện Quỳnh Lưu',
        "value": 'Huyện Quỳnh Lưu',
        "parent": 'Tỉnh Nghệ An'
    },
    {
        "name": 'Huyện Con Cuông',
        "value": 'Huyện Con Cuông',
        "parent": 'Tỉnh Nghệ An'
    },
    {
        "name": 'Huyện Tân Kỳ',
        "value": 'Huyện Tân Kỳ',
        "parent": 'Tỉnh Nghệ An'
    },
    {
        "name": 'Huyện Anh Sơn',
        "value": 'Huyện Anh Sơn',
        "parent": 'Tỉnh Nghệ An'
    },
    {
        "name": 'Huyện Diễn Châu',
        "value": 'Huyện Diễn Châu',
        "parent": 'Tỉnh Nghệ An'
    },
    {
        "name": 'Huyện Yên Thành',
        "value": 'Huyện Yên Thành',
        "parent": 'Tỉnh Nghệ An'
    },
    {
        "name": 'Huyện Đô Lương',
        "value": 'Huyện Đô Lương',
        "parent": 'Tỉnh Nghệ An'
    },
    {
        "name": 'Huyện Thanh Chương',
        "value": 'Huyện Thanh Chương',
        "parent": 'Tỉnh Nghệ An'
    },
    {
        "name": 'Huyện Nghi Lộc',
        "value": 'Huyện Nghi Lộc',
        "parent": 'Tỉnh Nghệ An'
    },
    {
        "name": 'Huyện Nam Đàn',
        "value": 'Huyện Nam Đàn',
        "parent": 'Tỉnh Nghệ An'
    },
    {
        "name": 'Huyện Hưng Nguyên',
        "value": 'Huyện Hưng Nguyên',
        "parent": 'Tỉnh Nghệ An'
    },
    {
        "name": 'Thị xã Hoàng Mai',
        "value": 'Thị xã Hoàng Mai',
        "parent": 'Tỉnh Nghệ An'
    },
    {
        "name": 'Thành phố Hà Tĩnh',
        "value": 'Thành phố Hà Tĩnh',
        "parent": 'Tỉnh Hà Tĩnh'
    },
    {
        "name": 'Thị xã Hồng Lĩnh',
        "value": 'Thị xã Hồng Lĩnh',
        "parent": 'Tỉnh Hà Tĩnh'
    },
    {
        "name": 'Huyện Hương Sơn',
        "value": 'Huyện Hương Sơn',
        "parent": 'Tỉnh Hà Tĩnh'
    },
    {
        "name": 'Huyện Đức Thọ',
        "value": 'Huyện Đức Thọ',
        "parent": 'Tỉnh Hà Tĩnh'
    },
    {
        "name": 'Huyện Vũ Quang',
        "value": 'Huyện Vũ Quang',
        "parent": 'Tỉnh Hà Tĩnh'
    },
    {
        "name": 'Huyện Nghi Xuân',
        "value": 'Huyện Nghi Xuân',
        "parent": 'Tỉnh Hà Tĩnh'
    },
    {
        "name": 'Huyện Can Lộc',
        "value": 'Huyện Can Lộc',
        "parent": 'Tỉnh Hà Tĩnh'
    },
    {
        "name": 'Huyện Hương Khê',
        "value": 'Huyện Hương Khê',
        "parent": 'Tỉnh Hà Tĩnh'
    },
    {
        "name": 'Huyện Thạch Hà',
        "value": 'Huyện Thạch Hà',
        "parent": 'Tỉnh Hà Tĩnh'
    },
    {
        "name": 'Huyện Cẩm Xuyên',
        "value": 'Huyện Cẩm Xuyên',
        "parent": 'Tỉnh Hà Tĩnh'
    },
    {
        "name": 'Huyện Kỳ Anh',
        "value": 'Huyện Kỳ Anh',
        "parent": 'Tỉnh Hà Tĩnh'
    },
    {
        "name": 'Huyện Lộc Hà',
        "value": 'Huyện Lộc Hà',
        "parent": 'Tỉnh Hà Tĩnh'
    },
    {
        "name": 'Thị xã Kỳ Anh',
        "value": 'Thị xã Kỳ Anh',
        "parent": 'Tỉnh Hà Tĩnh'
    },
    {
        "name": 'Thành Phố Đồng Hới',
        "value": 'Thành Phố Đồng Hới',
        "parent": 'Tỉnh Quảng Bình'
    },
    {
        "name": 'Huyện Minh Hóa',
        "value": 'Huyện Minh Hóa',
        "parent": 'Tỉnh Quảng Bình'
    },
    {
        "name": 'Huyện Tuyên Hóa',
        "value": 'Huyện Tuyên Hóa',
        "parent": 'Tỉnh Quảng Bình'
    },
    {
        "name": 'Huyện Quảng Trạch',
        "value": 'Huyện Quảng Trạch',
        "parent": 'Tỉnh Quảng Bình'
    },
    {
        "name": 'Huyện Bố Trạch',
        "value": 'Huyện Bố Trạch',
        "parent": 'Tỉnh Quảng Bình'
    },
    {
        "name": 'Huyện Quảng Ninh',
        "value": 'Huyện Quảng Ninh',
        "parent": 'Tỉnh Quảng Bình'
    },
    {
        "name": 'Huyện Lệ Thủy',
        "value": 'Huyện Lệ Thủy',
        "parent": 'Tỉnh Quảng Bình'
    },
    {
        "name": 'Thị xã Ba Đồn',
        "value": 'Thị xã Ba Đồn',
        "parent": 'Tỉnh Quảng Bình'
    },
    {
        "name": 'Thành phố Đông Hà',
        "value": 'Thành phố Đông Hà',
        "parent": 'Tỉnh Quảng Trị'
    },
    {
        "name": 'Thị xã Quảng Trị',
        "value": 'Thị xã Quảng Trị',
        "parent": 'Tỉnh Quảng Trị'
    },
    {
        "name": 'Huyện Vĩnh Linh',
        "value": 'Huyện Vĩnh Linh',
        "parent": 'Tỉnh Quảng Trị'
    },
    {
        "name": 'Huyện Hướng Hóa',
        "value": 'Huyện Hướng Hóa',
        "parent": 'Tỉnh Quảng Trị'
    },
    {
        "name": 'Huyện Gio Linh',
        "value": 'Huyện Gio Linh',
        "parent": 'Tỉnh Quảng Trị'
    },
    {
        "name": 'Huyện Đa Krông',
        "value": 'Huyện Đa Krông',
        "parent": 'Tỉnh Quảng Trị'
    },
    {
        "name": 'Huyện Cam Lộ',
        "value": 'Huyện Cam Lộ',
        "parent": 'Tỉnh Quảng Trị'
    },
    {
        "name": 'Huyện Triệu Phong',
        "value": 'Huyện Triệu Phong',
        "parent": 'Tỉnh Quảng Trị'
    },
    {
        "name": 'Huyện Hải Lăng',
        "value": 'Huyện Hải Lăng',
        "parent": 'Tỉnh Quảng Trị'
    },
    {
        "name": 'Huyện Cồn Cỏ',
        "value": 'Huyện Cồn Cỏ',
        "parent": 'Tỉnh Quảng Trị'
    },
    {
        "name": 'Thành phố Huế',
        "value": 'Thành phố Huế',
        "parent": 'Tỉnh Thừa Thiên Huế'
    },
    {
        "name": 'Huyện Phong Điền',
        "value": 'Huyện Phong Điền',
        "parent": 'Tỉnh Thừa Thiên Huế'
    },
    {
        "name": 'Huyện Quảng Điền',
        "value": 'Huyện Quảng Điền',
        "parent": 'Tỉnh Thừa Thiên Huế'
    },
    {
        "name": 'Huyện Phú Vang',
        "value": 'Huyện Phú Vang',
        "parent": 'Tỉnh Thừa Thiên Huế'
    },
    {
        "name": 'Thị xã Hương Thủy',
        "value": 'Thị xã Hương Thủy',
        "parent": 'Tỉnh Thừa Thiên Huế'
    },
    {
        "name": 'Thị xã Hương Trà',
        "value": 'Thị xã Hương Trà',
        "parent": 'Tỉnh Thừa Thiên Huế'
    },
    {
        "name": 'Huyện A Lưới',
        "value": 'Huyện A Lưới',
        "parent": 'Tỉnh Thừa Thiên Huế'
    },
    {
        "name": 'Huyện Phú Lộc',
        "value": 'Huyện Phú Lộc',
        "parent": 'Tỉnh Thừa Thiên Huế'
    },
    {
        "name": 'Huyện Nam Đông',
        "value": 'Huyện Nam Đông',
        "parent": 'Tỉnh Thừa Thiên Huế'
    },
    {
        "name": 'Quận Liên Chiểu',
        "value": 'Quận Liên Chiểu',
        "parent": 'Thành phố Đà Nẵng'
    },
    {
        "name": 'Quận Thanh Khê',
        "value": 'Quận Thanh Khê',
        "parent": 'Thành phố Đà Nẵng'
    },
    {
        "name": 'Quận Hải Châu',
        "value": 'Quận Hải Châu',
        "parent": 'Thành phố Đà Nẵng'
    },
    {
        "name": 'Quận Sơn Trà',
        "value": 'Quận Sơn Trà',
        "parent": 'Thành phố Đà Nẵng'
    },
    {
        "name": 'Quận Ngũ Hành Sơn',
        "value": 'Quận Ngũ Hành Sơn',
        "parent": 'Thành phố Đà Nẵng'
    },
    {
        "name": 'Quận Cẩm Lệ',
        "value": 'Quận Cẩm Lệ',
        "parent": 'Thành phố Đà Nẵng'
    },
    {
        "name": 'Huyện Hòa Vang',
        "value": 'Huyện Hòa Vang',
        "parent": 'Thành phố Đà Nẵng'
    },
    {
        "name": 'Huyện Hoàng Sa',
        "value": 'Huyện Hoàng Sa',
        "parent": 'Thành phố Đà Nẵng'
    },
    {
        "name": 'Thành phố Tam Kỳ',
        "value": 'Thành phố Tam Kỳ',
        "parent": 'Tỉnh Quảng Nam'
    },
    {
        "name": 'Thành phố Hội An',
        "value": 'Thành phố Hội An',
        "parent": 'Tỉnh Quảng Nam'
    },
    {
        "name": 'Huyện Tây Giang',
        "value": 'Huyện Tây Giang',
        "parent": 'Tỉnh Quảng Nam'
    },
    {
        "name": 'Huyện Đông Giang',
        "value": 'Huyện Đông Giang',
        "parent": 'Tỉnh Quảng Nam'
    },
    {
        "name": 'Huyện Đại Lộc',
        "value": 'Huyện Đại Lộc',
        "parent": 'Tỉnh Quảng Nam'
    },
    {
        "name": 'Thị xã Điện Bàn',
        "value": 'Thị xã Điện Bàn',
        "parent": 'Tỉnh Quảng Nam'
    },
    {
        "name": 'Huyện Duy Xuyên',
        "value": 'Huyện Duy Xuyên',
        "parent": 'Tỉnh Quảng Nam'
    },
    {
        "name": 'Huyện Quế Sơn',
        "value": 'Huyện Quế Sơn',
        "parent": 'Tỉnh Quảng Nam'
    },
    {
        "name": 'Huyện Nam Giang',
        "value": 'Huyện Nam Giang',
        "parent": 'Tỉnh Quảng Nam'
    },
    {
        "name": 'Huyện Phước Sơn',
        "value": 'Huyện Phước Sơn',
        "parent": 'Tỉnh Quảng Nam'
    },
    {
        "name": 'Huyện Hiệp Đức',
        "value": 'Huyện Hiệp Đức',
        "parent": 'Tỉnh Quảng Nam'
    },
    {
        "name": 'Huyện Thăng Bình',
        "value": 'Huyện Thăng Bình',
        "parent": 'Tỉnh Quảng Nam'
    },
    {
        "name": 'Huyện Tiên Phước',
        "value": 'Huyện Tiên Phước',
        "parent": 'Tỉnh Quảng Nam'
    },
    {
        "name": 'Huyện Bắc Trà My',
        "value": 'Huyện Bắc Trà My',
        "parent": 'Tỉnh Quảng Nam'
    },
    {
        "name": 'Huyện Nam Trà My',
        "value": 'Huyện Nam Trà My',
        "parent": 'Tỉnh Quảng Nam'
    },
    {
        "name": 'Huyện Núi Thành',
        "value": 'Huyện Núi Thành',
        "parent": 'Tỉnh Quảng Nam'
    },
    {
        "name": 'Huyện Phú Ninh',
        "value": 'Huyện Phú Ninh',
        "parent": 'Tỉnh Quảng Nam'
    },
    {
        "name": 'Huyện Nông Sơn',
        "value": 'Huyện Nông Sơn',
        "parent": 'Tỉnh Quảng Nam'
    },
    {
        "name": 'Thành phố Quảng Ngãi',
        "value": 'Thành phố Quảng Ngãi',
        "parent": 'Tỉnh Quảng Ngãi'
    },
    {
        "name": 'Huyện Bình Sơn',
        "value": 'Huyện Bình Sơn',
        "parent": 'Tỉnh Quảng Ngãi'
    },
    {
        "name": 'Huyện Trà Bồng',
        "value": 'Huyện Trà Bồng',
        "parent": 'Tỉnh Quảng Ngãi'
    },
    {
        "name": 'Huyện Sơn Tịnh',
        "value": 'Huyện Sơn Tịnh',
        "parent": 'Tỉnh Quảng Ngãi'
    },
    {
        "name": 'Huyện Tư Nghĩa',
        "value": 'Huyện Tư Nghĩa',
        "parent": 'Tỉnh Quảng Ngãi'
    },
    {
        "name": 'Huyện Sơn Hà',
        "value": 'Huyện Sơn Hà',
        "parent": 'Tỉnh Quảng Ngãi'
    },
    {
        "name": 'Huyện Sơn Tây',
        "value": 'Huyện Sơn Tây',
        "parent": 'Tỉnh Quảng Ngãi'
    },
    {
        "name": 'Huyện Minh Long',
        "value": 'Huyện Minh Long',
        "parent": 'Tỉnh Quảng Ngãi'
    },
    {
        "name": 'Huyện Nghĩa Hành',
        "value": 'Huyện Nghĩa Hành',
        "parent": 'Tỉnh Quảng Ngãi'
    },
    {
        "name": 'Huyện Mộ Đức',
        "value": 'Huyện Mộ Đức',
        "parent": 'Tỉnh Quảng Ngãi'
    },
    {
        "name": 'Thị xã Đức Phổ',
        "value": 'Thị xã Đức Phổ',
        "parent": 'Tỉnh Quảng Ngãi'
    },
    {
        "name": 'Huyện Ba Tơ',
        "value": 'Huyện Ba Tơ',
        "parent": 'Tỉnh Quảng Ngãi'
    },
    {
        "name": 'Huyện Lý Sơn',
        "value": 'Huyện Lý Sơn',
        "parent": 'Tỉnh Quảng Ngãi'
    },
    {
        "name": 'Thành phố Qui Nhơn',
        "value": 'Thành phố Qui Nhơn',
        "parent": 'Tỉnh Bình Định'
    },
    {
        "name": 'Huyện An Lão',
        "value": 'Huyện An Lão',
        "parent": 'Tỉnh Bình Định'
    },
    {
        "name": 'Thị xã Hoài Nhơn',
        "value": 'Thị xã Hoài Nhơn',
        "parent": 'Tỉnh Bình Định'
    },
    {
        "name": 'Huyện Hoài Ân',
        "value": 'Huyện Hoài Ân',
        "parent": 'Tỉnh Bình Định'
    },
    {
        "name": 'Huyện Phù Mỹ',
        "value": 'Huyện Phù Mỹ',
        "parent": 'Tỉnh Bình Định'
    },
    {
        "name": 'Huyện Vĩnh Thạnh',
        "value": 'Huyện Vĩnh Thạnh',
        "parent": 'Tỉnh Bình Định'
    },
    {
        "name": 'Huyện Tây Sơn',
        "value": 'Huyện Tây Sơn',
        "parent": 'Tỉnh Bình Định'
    },
    {
        "name": 'Huyện Phù Cát',
        "value": 'Huyện Phù Cát',
        "parent": 'Tỉnh Bình Định'
    },
    {
        "name": 'Thị xã An Nhơn',
        "value": 'Thị xã An Nhơn',
        "parent": 'Tỉnh Bình Định'
    },
    {
        "name": 'Huyện Tuy Phước',
        "value": 'Huyện Tuy Phước',
        "parent": 'Tỉnh Bình Định'
    },
    {
        "name": 'Huyện Vân Canh',
        "value": 'Huyện Vân Canh',
        "parent": 'Tỉnh Bình Định'
    },
    {
        "name": 'Thành phố Tuy Hoà',
        "value": 'Thành phố Tuy Hoà',
        "parent": 'Tỉnh Phú Yên'
    },
    {
        "name": 'Thị xã Sông Cầu',
        "value": 'Thị xã Sông Cầu',
        "parent": 'Tỉnh Phú Yên'
    },
    {
        "name": 'Huyện Đồng Xuân',
        "value": 'Huyện Đồng Xuân',
        "parent": 'Tỉnh Phú Yên'
    },
    {
        "name": 'Huyện Tuy An',
        "value": 'Huyện Tuy An',
        "parent": 'Tỉnh Phú Yên'
    },
    {
        "name": 'Huyện Sơn Hòa',
        "value": 'Huyện Sơn Hòa',
        "parent": 'Tỉnh Phú Yên'
    },
    {
        "name": 'Huyện Sông Hinh',
        "value": 'Huyện Sông Hinh',
        "parent": 'Tỉnh Phú Yên'
    },
    {
        "name": 'Huyện Tây Hoà',
        "value": 'Huyện Tây Hoà',
        "parent": 'Tỉnh Phú Yên'
    },
    {
        "name": 'Huyện Phú Hoà',
        "value": 'Huyện Phú Hoà',
        "parent": 'Tỉnh Phú Yên'
    },
    {
        "name": 'Thị xã Đông Hòa',
        "value": 'Thị xã Đông Hòa',
        "parent": 'Tỉnh Phú Yên'
    },
    {
        "name": 'Thành phố Nha Trang',
        "value": 'Thành phố Nha Trang',
        "parent": 'Tỉnh Khánh Hòa'
    },
    {
        "name": 'Thành phố Cam Ranh',
        "value": 'Thành phố Cam Ranh',
        "parent": 'Tỉnh Khánh Hòa'
    },
    {
        "name": 'Huyện Cam Lâm',
        "value": 'Huyện Cam Lâm',
        "parent": 'Tỉnh Khánh Hòa'
    },
    {
        "name": 'Huyện Vạn Ninh',
        "value": 'Huyện Vạn Ninh',
        "parent": 'Tỉnh Khánh Hòa'
    },
    {
        "name": 'Thị xã Ninh Hòa',
        "value": 'Thị xã Ninh Hòa',
        "parent": 'Tỉnh Khánh Hòa'
    },
    {
        "name": 'Huyện Khánh Vĩnh',
        "value": 'Huyện Khánh Vĩnh',
        "parent": 'Tỉnh Khánh Hòa'
    },
    {
        "name": 'Huyện Diên Khánh',
        "value": 'Huyện Diên Khánh',
        "parent": 'Tỉnh Khánh Hòa'
    },
    {
        "name": 'Huyện Khánh Sơn',
        "value": 'Huyện Khánh Sơn',
        "parent": 'Tỉnh Khánh Hòa'
    },
    {
        "name": 'Huyện Trường Sa',
        "value": 'Huyện Trường Sa',
        "parent": 'Tỉnh Khánh Hòa'
    },
    {
        "name": 'Thành phố Phan Rang-Tháp Chàm',
        "value": 'Thành phố Phan Rang-Tháp Chàm',
        "parent": 'Tỉnh Ninh Thuận'
    },
    {
        "name": 'Huyện Bác Ái',
        "value": 'Huyện Bác Ái',
        "parent": 'Tỉnh Ninh Thuận'
    },
    {
        "name": 'Huyện Ninh Sơn',
        "value": 'Huyện Ninh Sơn',
        "parent": 'Tỉnh Ninh Thuận'
    },
    {
        "name": 'Huyện Ninh Hải',
        "value": 'Huyện Ninh Hải',
        "parent": 'Tỉnh Ninh Thuận'
    },
    {
        "name": 'Huyện Ninh Phước',
        "value": 'Huyện Ninh Phước',
        "parent": 'Tỉnh Ninh Thuận'
    },
    {
        "name": 'Huyện Thuận Bắc',
        "value": 'Huyện Thuận Bắc',
        "parent": 'Tỉnh Ninh Thuận'
    },
    {
        "name": 'Huyện Thuận Nam',
        "value": 'Huyện Thuận Nam',
        "parent": 'Tỉnh Ninh Thuận'
    },
    {
        "name": 'Thành phố Phan Thiết',
        "value": 'Thành phố Phan Thiết',
        "parent": 'Tỉnh Bình Thuận'
    },
    {
        "name": 'Thị xã La Gi',
        "value": 'Thị xã La Gi',
        "parent": 'Tỉnh Bình Thuận'
    },
    {
        "name": 'Huyện Tuy Phong',
        "value": 'Huyện Tuy Phong',
        "parent": 'Tỉnh Bình Thuận'
    },
    {
        "name": 'Huyện Bắc Bình',
        "value": 'Huyện Bắc Bình',
        "parent": 'Tỉnh Bình Thuận'
    },
    {
        "name": 'Huyện Hàm Thuận Bắc',
        "value": 'Huyện Hàm Thuận Bắc',
        "parent": 'Tỉnh Bình Thuận'
    },
    {
        "name": 'Huyện Hàm Thuận Nam',
        "value": 'Huyện Hàm Thuận Nam',
        "parent": 'Tỉnh Bình Thuận'
    },
    {
        "name": 'Huyện Tánh Linh',
        "value": 'Huyện Tánh Linh',
        "parent": 'Tỉnh Bình Thuận'
    },
    {
        "name": 'Huyện Đức Linh',
        "value": 'Huyện Đức Linh',
        "parent": 'Tỉnh Bình Thuận'
    },
    {
        "name": 'Huyện Hàm Tân',
        "value": 'Huyện Hàm Tân',
        "parent": 'Tỉnh Bình Thuận'
    },
    {
        "name": 'Huyện Phú Quí',
        "value": 'Huyện Phú Quí',
        "parent": 'Tỉnh Bình Thuận'
    },
    {
        "name": 'Thành phố Kon Tum',
        "value": 'Thành phố Kon Tum',
        "parent": 'Tỉnh Kon Tum'
    },
    {
        "name": 'Huyện Đắk Glei',
        "value": 'Huyện Đắk Glei',
        "parent": 'Tỉnh Kon Tum'
    },
    {
        "name": 'Huyện Ngọc Hồi',
        "value": 'Huyện Ngọc Hồi',
        "parent": 'Tỉnh Kon Tum'
    },
    {
        "name": 'Huyện Đắk Tô',
        "value": 'Huyện Đắk Tô',
        "parent": 'Tỉnh Kon Tum'
    },
    {
        "name": 'Huyện Kon Plông',
        "value": 'Huyện Kon Plông',
        "parent": 'Tỉnh Kon Tum'
    },
    {
        "name": 'Huyện Kon Rẫy',
        "value": 'Huyện Kon Rẫy',
        "parent": 'Tỉnh Kon Tum'
    },
    {
        "name": 'Huyện Đắk Hà',
        "value": 'Huyện Đắk Hà',
        "parent": 'Tỉnh Kon Tum'
    },
    {
        "name": 'Huyện Sa Thầy',
        "value": 'Huyện Sa Thầy',
        "parent": 'Tỉnh Kon Tum'
    },
    {
        "name": 'Huyện Tu Mơ Rông',
        "value": 'Huyện Tu Mơ Rông',
        "parent": 'Tỉnh Kon Tum'
    },
    {
        "name": "Huyện Ia H' Drai",
        "value": "Huyện Ia H' Drai",
        "parent": 'Tỉnh Kon Tum'
    },
    {
        "name": 'Thành phố Pleiku',
        "value": 'Thành phố Pleiku',
        "parent": 'Tỉnh Gia Lai'
    },
    {
        "name": 'Thị xã An Khê',
        "value": 'Thị xã An Khê',
        "parent": 'Tỉnh Gia Lai'
    },
    {
        "name": 'Thị xã Ayun Pa',
        "value": 'Thị xã Ayun Pa',
        "parent": 'Tỉnh Gia Lai'
    },
    {
        "name": 'Huyện KBang',
        "value": 'Huyện KBang',
        "parent": 'Tỉnh Gia Lai'
    },
    {
        "name": 'Huyện Đăk Đoa',
        "value": 'Huyện Đăk Đoa',
        "parent": 'Tỉnh Gia Lai'
    },
    {
        "name": 'Huyện Chư Păh',
        "value": 'Huyện Chư Păh',
        "parent": 'Tỉnh Gia Lai'
    },
    {
        "name": 'Huyện Ia Grai',
        "value": 'Huyện Ia Grai',
        "parent": 'Tỉnh Gia Lai'
    },
    {
        "name": 'Huyện Mang Yang',
        "value": 'Huyện Mang Yang',
        "parent": 'Tỉnh Gia Lai'
    },
    {
        "name": 'Huyện Kông Chro',
        "value": 'Huyện Kông Chro',
        "parent": 'Tỉnh Gia Lai'
    },
    {
        "name": 'Huyện Đức Cơ',
        "value": 'Huyện Đức Cơ',
        "parent": 'Tỉnh Gia Lai'
    },
    {
        "name": 'Huyện Chư Prông',
        "value": 'Huyện Chư Prông',
        "parent": 'Tỉnh Gia Lai'
    },
    {
        "name": 'Huyện Chư Sê',
        "value": 'Huyện Chư Sê',
        "parent": 'Tỉnh Gia Lai'
    },
    {
        "name": 'Huyện Đăk Pơ',
        "value": 'Huyện Đăk Pơ',
        "parent": 'Tỉnh Gia Lai'
    },
    {
        "name": 'Huyện Ia Pa',
        "value": 'Huyện Ia Pa',
        "parent": 'Tỉnh Gia Lai'
    },
    {
        "name": 'Huyện Krông Pa',
        "value": 'Huyện Krông Pa',
        "parent": 'Tỉnh Gia Lai'
    },
    {
        "name": 'Huyện Phú Thiện',
        "value": 'Huyện Phú Thiện',
        "parent": 'Tỉnh Gia Lai'
    },
    {
        "name": 'Huyện Chư Pưh',
        "value": 'Huyện Chư Pưh',
        "parent": 'Tỉnh Gia Lai'
    },
    {
        "name": 'Thành phố Buôn Ma Thuột',
        "value": 'Thành phố Buôn Ma Thuột',
        "parent": 'Tỉnh Đắk Lắk'
    },
    {
        "name": 'Thị Xã Buôn Hồ',
        "value": 'Thị Xã Buôn Hồ',
        "parent": 'Tỉnh Đắk Lắk'
    },
    {
        "name": "Huyện Ea H'leo",
        "value": "Huyện Ea H'leo",
        "parent": 'Tỉnh Đắk Lắk'
    },
    {
        "name": 'Huyện Ea Súp',
        "value": 'Huyện Ea Súp',
        "parent": 'Tỉnh Đắk Lắk'
    },
    {
        "name": 'Huyện Buôn Đôn',
        "value": 'Huyện Buôn Đôn',
        "parent": 'Tỉnh Đắk Lắk'
    },
    {
        "name": "Huyện Cư M'gar",
        "value": "Huyện Cư M'gar",
        "parent": 'Tỉnh Đắk Lắk'
    },
    {
        "name": 'Huyện Krông Búk',
        "value": 'Huyện Krông Búk',
        "parent": 'Tỉnh Đắk Lắk'
    },
    {
        "name": 'Huyện Krông Năng',
        "value": 'Huyện Krông Năng',
        "parent": 'Tỉnh Đắk Lắk'
    },
    {
        "name": 'Huyện Ea Kar',
        "value": 'Huyện Ea Kar',
        "parent": 'Tỉnh Đắk Lắk'
    },
    {
        "name": "Huyện M'Đrắk",
        "value": "Huyện M'Đrắk",
        "parent": 'Tỉnh Đắk Lắk'
    },
    {
        "name": 'Huyện Krông Bông',
        "value": 'Huyện Krông Bông',
        "parent": 'Tỉnh Đắk Lắk'
    },
    {
        "name": 'Huyện Krông Pắc',
        "value": 'Huyện Krông Pắc',
        "parent": 'Tỉnh Đắk Lắk'
    },
    {
        "name": 'Huyện Krông A Na',
        "value": 'Huyện Krông A Na',
        "parent": 'Tỉnh Đắk Lắk'
    },
    {
        "name": 'Huyện Lắk',
        "value": 'Huyện Lắk',
        "parent": 'Tỉnh Đắk Lắk'
    },
    {
        "name": 'Huyện Cư Kuin',
        "value": 'Huyện Cư Kuin',
        "parent": 'Tỉnh Đắk Lắk'
    },
    {
        "name": 'Thành phố Gia Nghĩa',
        "value": 'Thành phố Gia Nghĩa',
        "parent": 'Tỉnh Đắk Nông'
    },
    {
        "name": 'Huyện Đăk Glong',
        "value": 'Huyện Đăk Glong',
        "parent": 'Tỉnh Đắk Nông'
    },
    {
        "name": 'Huyện Cư Jút',
        "value": 'Huyện Cư Jút',
        "parent": 'Tỉnh Đắk Nông'
    },
    {
        "name": 'Huyện Đắk Mil',
        "value": 'Huyện Đắk Mil',
        "parent": 'Tỉnh Đắk Nông'
    },
    {
        "name": 'Huyện Krông Nô',
        "value": 'Huyện Krông Nô',
        "parent": 'Tỉnh Đắk Nông'
    },
    {
        "name": 'Huyện Đắk Song',
        "value": 'Huyện Đắk Song',
        "parent": 'Tỉnh Đắk Nông'
    },
    {
        "name": "Huyện Đắk R'Lấp",
        "value": "Huyện Đắk R'Lấp",
        "parent": 'Tỉnh Đắk Nông'
    },
    {
        "name": 'Huyện Tuy Đức',
        "value": 'Huyện Tuy Đức',
        "parent": 'Tỉnh Đắk Nông'
    },
    {
        "name": 'Thành phố Đà Lạt',
        "value": 'Thành phố Đà Lạt',
        "parent": 'Tỉnh Lâm Đồng'
    },
    {
        "name": 'Thành phố Bảo Lộc',
        "value": 'Thành phố Bảo Lộc',
        "parent": 'Tỉnh Lâm Đồng'
    },
    {
        "name": 'Huyện Đam Rông',
        "value": 'Huyện Đam Rông',
        "parent": 'Tỉnh Lâm Đồng'
    },
    {
        "name": 'Huyện Lạc Dương',
        "value": 'Huyện Lạc Dương',
        "parent": 'Tỉnh Lâm Đồng'
    },
    {
        "name": 'Huyện Lâm Hà',
        "value": 'Huyện Lâm Hà',
        "parent": 'Tỉnh Lâm Đồng'
    },
    {
        "name": 'Huyện Đơn Dương',
        "value": 'Huyện Đơn Dương',
        "parent": 'Tỉnh Lâm Đồng'
    },
    {
        "name": 'Huyện Đức Trọng',
        "value": 'Huyện Đức Trọng',
        "parent": 'Tỉnh Lâm Đồng'
    },
    {
        "name": 'Huyện Di Linh',
        "value": 'Huyện Di Linh',
        "parent": 'Tỉnh Lâm Đồng'
    },
    {
        "name": 'Huyện Bảo Lâm',
        "value": 'Huyện Bảo Lâm',
        "parent": 'Tỉnh Lâm Đồng'
    },
    {
        "name": 'Huyện Đạ Huoai',
        "value": 'Huyện Đạ Huoai',
        "parent": 'Tỉnh Lâm Đồng'
    },
    {
        "name": 'Huyện Đạ Tẻh',
        "value": 'Huyện Đạ Tẻh',
        "parent": 'Tỉnh Lâm Đồng'
    },
    {
        "name": 'Huyện Cát Tiên',
        "value": 'Huyện Cát Tiên',
        "parent": 'Tỉnh Lâm Đồng'
    },
    {
        "name": 'Thị xã Phước Long',
        "value": 'Thị xã Phước Long',
        "parent": 'Tỉnh Bình Phước'
    },
    {
        "name": 'Thành phố Đồng Xoài',
        "value": 'Thành phố Đồng Xoài',
        "parent": 'Tỉnh Bình Phước'
    },
    {
        "name": 'Thị xã Bình Long',
        "value": 'Thị xã Bình Long',
        "parent": 'Tỉnh Bình Phước'
    },
    {
        "name": 'Huyện Bù Gia Mập',
        "value": 'Huyện Bù Gia Mập',
        "parent": 'Tỉnh Bình Phước'
    },
    {
        "name": 'Huyện Lộc Ninh',
        "value": 'Huyện Lộc Ninh',
        "parent": 'Tỉnh Bình Phước'
    },
    {
        "name": 'Huyện Bù Đốp',
        "value": 'Huyện Bù Đốp',
        "parent": 'Tỉnh Bình Phước'
    },
    {
        "name": 'Huyện Hớn Quản',
        "value": 'Huyện Hớn Quản',
        "parent": 'Tỉnh Bình Phước'
    },
    {
        "name": 'Huyện Đồng Phú',
        "value": 'Huyện Đồng Phú',
        "parent": 'Tỉnh Bình Phước'
    },
    {
        "name": 'Huyện Bù Đăng',
        "value": 'Huyện Bù Đăng',
        "parent": 'Tỉnh Bình Phước'
    },
    {
        "name": 'Huyện Chơn Thành',
        "value": 'Huyện Chơn Thành',
        "parent": 'Tỉnh Bình Phước'
    },
    {
        "name": 'Huyện Phú Riềng',
        "value": 'Huyện Phú Riềng',
        "parent": 'Tỉnh Bình Phước'
    },
    {
        "name": 'Thành phố Tây Ninh',
        "value": 'Thành phố Tây Ninh',
        "parent": 'Tỉnh Tây Ninh'
    },
    {
        "name": 'Huyện Tân Biên',
        "value": 'Huyện Tân Biên',
        "parent": 'Tỉnh Tây Ninh'
    },
    {
        "name": 'Huyện Tân Châu',
        "value": 'Huyện Tân Châu',
        "parent": 'Tỉnh Tây Ninh'
    },
    {
        "name": 'Huyện Dương Minh Châu',
        "value": 'Huyện Dương Minh Châu',
        "parent": 'Tỉnh Tây Ninh'
    },
    {
        "name": 'Huyện Châu Thành',
        "value": 'Huyện Châu Thành',
        "parent": 'Tỉnh Tây Ninh'
    },
    {
        "name": 'Thị xã Hòa Thành',
        "value": 'Thị xã Hòa Thành',
        "parent": 'Tỉnh Tây Ninh'
    },
    {
        "name": 'Huyện Gò Dầu',
        "value": 'Huyện Gò Dầu',
        "parent": 'Tỉnh Tây Ninh'
    },
    {
        "name": 'Huyện Bến Cầu',
        "value": 'Huyện Bến Cầu',
        "parent": 'Tỉnh Tây Ninh'
    },
    {
        "name": 'Thị xã Trảng Bàng',
        "value": 'Thị xã Trảng Bàng',
        "parent": 'Tỉnh Tây Ninh'
    },
    {
        "name": 'Thành phố Thủ Dầu Một',
        "value": 'Thành phố Thủ Dầu Một',
        "parent": 'Tỉnh Bình Dương'
    },
    {
        "name": 'Huyện Bàu Bàng',
        "value": 'Huyện Bàu Bàng',
        "parent": 'Tỉnh Bình Dương'
    },
    {
        "name": 'Huyện Dầu Tiếng',
        "value": 'Huyện Dầu Tiếng',
        "parent": 'Tỉnh Bình Dương'
    },
    {
        "name": 'Thị xã Bến Cát',
        "value": 'Thị xã Bến Cát',
        "parent": 'Tỉnh Bình Dương'
    },
    {
        "name": 'Huyện Phú Giáo',
        "value": 'Huyện Phú Giáo',
        "parent": 'Tỉnh Bình Dương'
    },
    {
        "name": 'Thị xã Tân Uyên',
        "value": 'Thị xã Tân Uyên',
        "parent": 'Tỉnh Bình Dương'
    },
    {
        "name": 'Thành phố Dĩ An',
        "value": 'Thành phố Dĩ An',
        "parent": 'Tỉnh Bình Dương'
    },
    {
        "name": 'Thành phố Thuận An',
        "value": 'Thành phố Thuận An',
        "parent": 'Tỉnh Bình Dương'
    },
    {
        "name": 'Huyện Bắc Tân Uyên',
        "value": 'Huyện Bắc Tân Uyên',
        "parent": 'Tỉnh Bình Dương'
    },
    {
        "name": 'Thành phố Biên Hòa',
        "value": 'Thành phố Biên Hòa',
        "parent": 'Tỉnh Đồng Nai'
    },
    {
        "name": 'Thành phố Long Khánh',
        "value": 'Thành phố Long Khánh',
        "parent": 'Tỉnh Đồng Nai'
    },
    {
        "name": 'Huyện Tân Phú',
        "value": 'Huyện Tân Phú',
        "parent": 'Tỉnh Đồng Nai'
    },
    {
        "name": 'Huyện Vĩnh Cửu',
        "value": 'Huyện Vĩnh Cửu',
        "parent": 'Tỉnh Đồng Nai'
    },
    {
        "name": 'Huyện Định Quán',
        "value": 'Huyện Định Quán',
        "parent": 'Tỉnh Đồng Nai'
    },
    {
        "name": 'Huyện Trảng Bom',
        "value": 'Huyện Trảng Bom',
        "parent": 'Tỉnh Đồng Nai'
    },
    {
        "name": 'Huyện Thống Nhất',
        "value": 'Huyện Thống Nhất',
        "parent": 'Tỉnh Đồng Nai'
    },
    {
        "name": 'Huyện Cẩm Mỹ',
        "value": 'Huyện Cẩm Mỹ',
        "parent": 'Tỉnh Đồng Nai'
    },
    {
        "name": 'Huyện Long Thành',
        "value": 'Huyện Long Thành',
        "parent": 'Tỉnh Đồng Nai'
    },
    {
        "name": 'Huyện Xuân Lộc',
        "value": 'Huyện Xuân Lộc',
        "parent": 'Tỉnh Đồng Nai'
    },
    {
        "name": 'Huyện Nhơn Trạch',
        "value": 'Huyện Nhơn Trạch',
        "parent": 'Tỉnh Đồng Nai'
    },
    {
        "name": 'Thành phố Vũng Tàu',
        "value": 'Thành phố Vũng Tàu',
        "parent": 'Tỉnh Bà Rịa - Vũng Tàu'
    },
    {
        "name": 'Thành phố Bà Rịa',
        "value": 'Thành phố Bà Rịa',
        "parent": 'Tỉnh Bà Rịa - Vũng Tàu'
    },
    {
        "name": 'Huyện Châu Đức',
        "value": 'Huyện Châu Đức',
        "parent": 'Tỉnh Bà Rịa - Vũng Tàu'
    },
    {
        "name": 'Huyện Xuyên Mộc',
        "value": 'Huyện Xuyên Mộc',
        "parent": 'Tỉnh Bà Rịa - Vũng Tàu'
    },
    {
        "name": 'Huyện Long Điền',
        "value": 'Huyện Long Điền',
        "parent": 'Tỉnh Bà Rịa - Vũng Tàu'
    },
    {
        "name": 'Huyện Đất Đỏ',
        "value": 'Huyện Đất Đỏ',
        "parent": 'Tỉnh Bà Rịa - Vũng Tàu'
    },
    {
        "name": 'Thị xã Phú Mỹ',
        "value": 'Thị xã Phú Mỹ',
        "parent": 'Tỉnh Bà Rịa - Vũng Tàu'
    },
    {
        "name": 'Huyện Côn Đảo',
        "value": 'Huyện Côn Đảo',
        "parent": 'Tỉnh Bà Rịa - Vũng Tàu'
    },
    {
        "name": 'Quận 1',
        "value": 'Quận 1',
        "parent": 'Thành phố Hồ Chí Minh'
    },
    {
        "name": 'Quận 12',
        "value": 'Quận 12',
        "parent": 'Thành phố Hồ Chí Minh'
    },
    {
        "name": 'Quận Thủ Đức',
        "value": 'Quận Thủ Đức',
        "parent": 'Thành phố Hồ Chí Minh'
    },
    {
        "name": 'Quận 9',
        "value": 'Quận 9',
        "parent": 'Thành phố Hồ Chí Minh'
    },
    {
        "name": 'Quận Gò Vấp',
        "value": 'Quận Gò Vấp',
        "parent": 'Thành phố Hồ Chí Minh'
    },
    {
        "name": 'Quận Bình Thạnh',
        "value": 'Quận Bình Thạnh',
        "parent": 'Thành phố Hồ Chí Minh'
    },
    {
        "name": 'Quận Tân Bình',
        "value": 'Quận Tân Bình',
        "parent": 'Thành phố Hồ Chí Minh'
    },
    {
        "name": 'Quận Tân Phú',
        "value": 'Quận Tân Phú',
        "parent": 'Thành phố Hồ Chí Minh'
    },
    {
        "name": 'Quận Phú Nhuận',
        "value": 'Quận Phú Nhuận',
        "parent": 'Thành phố Hồ Chí Minh'
    },
    {
        "name": 'Quận 2',
        "value": 'Quận 2',
        "parent": 'Thành phố Hồ Chí Minh'
    },
    {
        "name": 'Quận 3',
        "value": 'Quận 3',
        "parent": 'Thành phố Hồ Chí Minh'
    },
    {
        "name": 'Quận 10',
        "value": 'Quận 10',
        "parent": 'Thành phố Hồ Chí Minh'
    },
    {
        "name": 'Quận 11',
        "value": 'Quận 11',
        "parent": 'Thành phố Hồ Chí Minh'
    },
    {
        "name": 'Quận 4',
        "value": 'Quận 4',
        "parent": 'Thành phố Hồ Chí Minh'
    },
    {
        "name": 'Quận 5',
        "value": 'Quận 5',
        "parent": 'Thành phố Hồ Chí Minh'
    },
    {
        "name": 'Quận 6',
        "value": 'Quận 6',
        "parent": 'Thành phố Hồ Chí Minh'
    },
    {
        "name": 'Quận 8',
        "value": 'Quận 8',
        "parent": 'Thành phố Hồ Chí Minh'
    },
    {
        "name": 'Quận Bình Tân',
        "value": 'Quận Bình Tân',
        "parent": 'Thành phố Hồ Chí Minh'
    },
    {
        "name": 'Quận 7',
        "value": 'Quận 7',
        "parent": 'Thành phố Hồ Chí Minh'
    },
    {
        "name": 'Huyện Củ Chi',
        "value": 'Huyện Củ Chi',
        "parent": 'Thành phố Hồ Chí Minh'
    },
    {
        "name": 'Huyện Hóc Môn',
        "value": 'Huyện Hóc Môn',
        "parent": 'Thành phố Hồ Chí Minh'
    },
    {
        "name": 'Huyện Bình Chánh',
        "value": 'Huyện Bình Chánh',
        "parent": 'Thành phố Hồ Chí Minh'
    },
    {
        "name": 'Huyện Nhà Bè',
        "value": 'Huyện Nhà Bè',
        "parent": 'Thành phố Hồ Chí Minh'
    },
    {
        "name": 'Huyện Cần Giờ',
        "value": 'Huyện Cần Giờ',
        "parent": 'Thành phố Hồ Chí Minh'
    },
    {
        "name": 'Thành phố Tân An',
        "value": 'Thành phố Tân An',
        "parent": 'Tỉnh Long An'
    },
    {
        "name": 'Thị xã Kiến Tường',
        "value": 'Thị xã Kiến Tường',
        "parent": 'Tỉnh Long An'
    },
    {
        "name": 'Huyện Tân Hưng',
        "value": 'Huyện Tân Hưng',
        "parent": 'Tỉnh Long An'
    },
    {
        "name": 'Huyện Vĩnh Hưng',
        "value": 'Huyện Vĩnh Hưng',
        "parent": 'Tỉnh Long An'
    },
    {
        "name": 'Huyện Mộc Hóa',
        "value": 'Huyện Mộc Hóa',
        "parent": 'Tỉnh Long An'
    },
    {
        "name": 'Huyện Tân Thạnh',
        "value": 'Huyện Tân Thạnh',
        "parent": 'Tỉnh Long An'
    },
    {
        "name": 'Huyện Thạnh Hóa',
        "value": 'Huyện Thạnh Hóa',
        "parent": 'Tỉnh Long An'
    },
    {
        "name": 'Huyện Đức Huệ',
        "value": 'Huyện Đức Huệ',
        "parent": 'Tỉnh Long An'
    },
    {
        "name": 'Huyện Đức Hòa',
        "value": 'Huyện Đức Hòa',
        "parent": 'Tỉnh Long An'
    },
    {
        "name": 'Huyện Bến Lức',
        "value": 'Huyện Bến Lức',
        "parent": 'Tỉnh Long An'
    },
    {
        "name": 'Huyện Thủ Thừa',
        "value": 'Huyện Thủ Thừa',
        "parent": 'Tỉnh Long An'
    },
    {
        "name": 'Huyện Tân Trụ',
        "value": 'Huyện Tân Trụ',
        "parent": 'Tỉnh Long An'
    },
    {
        "name": 'Huyện Cần Đước',
        "value": 'Huyện Cần Đước',
        "parent": 'Tỉnh Long An'
    },
    {
        "name": 'Huyện Cần Giuộc',
        "value": 'Huyện Cần Giuộc',
        "parent": 'Tỉnh Long An'
    },
    {
        "name": 'Huyện Châu Thành',
        "value": 'Huyện Châu Thành',
        "parent": 'Tỉnh Long An'
    },
    {
        "name": 'Thành phố Mỹ Tho',
        "value": 'Thành phố Mỹ Tho',
        "parent": 'Tỉnh Tiền Giang'
    },
    {
        "name": 'Thị xã Gò Công',
        "value": 'Thị xã Gò Công',
        "parent": 'Tỉnh Tiền Giang'
    },
    {
        "name": 'Thị xã Cai Lậy',
        "value": 'Thị xã Cai Lậy',
        "parent": 'Tỉnh Tiền Giang'
    },
    {
        "name": 'Huyện Tân Phước',
        "value": 'Huyện Tân Phước',
        "parent": 'Tỉnh Tiền Giang'
    },
    {
        "name": 'Huyện Cái Bè',
        "value": 'Huyện Cái Bè',
        "parent": 'Tỉnh Tiền Giang'
    },
    {
        "name": 'Huyện Cai Lậy',
        "value": 'Huyện Cai Lậy',
        "parent": 'Tỉnh Tiền Giang'
    },
    {
        "name": 'Huyện Châu Thành',
        "value": 'Huyện Châu Thành',
        "parent": 'Tỉnh Tiền Giang'
    },
    {
        "name": 'Huyện Chợ Gạo',
        "value": 'Huyện Chợ Gạo',
        "parent": 'Tỉnh Tiền Giang'
    },
    {
        "name": 'Huyện Gò Công Tây',
        "value": 'Huyện Gò Công Tây',
        "parent": 'Tỉnh Tiền Giang'
    },
    {
        "name": 'Huyện Gò Công Đông',
        "value": 'Huyện Gò Công Đông',
        "parent": 'Tỉnh Tiền Giang'
    },
    {
        "name": 'Huyện Tân Phú Đông',
        "value": 'Huyện Tân Phú Đông',
        "parent": 'Tỉnh Tiền Giang'
    },
    {
        "name": 'Thành phố Bến Tre',
        "value": 'Thành phố Bến Tre',
        "parent": 'Tỉnh Bến Tre'
    },
    {
        "name": 'Huyện Châu Thành',
        "value": 'Huyện Châu Thành',
        "parent": 'Tỉnh Bến Tre'
    },
    {
        "name": 'Huyện Chợ Lách',
        "value": 'Huyện Chợ Lách',
        "parent": 'Tỉnh Bến Tre'
    },
    {
        "name": 'Huyện Mỏ Cày Nam',
        "value": 'Huyện Mỏ Cày Nam',
        "parent": 'Tỉnh Bến Tre'
    },
    {
        "name": 'Huyện Giồng Trôm',
        "value": 'Huyện Giồng Trôm',
        "parent": 'Tỉnh Bến Tre'
    },
    {
        "name": 'Huyện Bình Đại',
        "value": 'Huyện Bình Đại',
        "parent": 'Tỉnh Bến Tre'
    },
    {
        "name": 'Huyện Ba Tri',
        "value": 'Huyện Ba Tri',
        "parent": 'Tỉnh Bến Tre'
    },
    {
        "name": 'Huyện Thạnh Phú',
        "value": 'Huyện Thạnh Phú',
        "parent": 'Tỉnh Bến Tre'
    },
    {
        "name": 'Huyện Mỏ Cày Bắc',
        "value": 'Huyện Mỏ Cày Bắc',
        "parent": 'Tỉnh Bến Tre'
    },
    {
        "name": 'Thành phố Trà Vinh',
        "value": 'Thành phố Trà Vinh',
        "parent": 'Tỉnh Trà Vinh'
    },
    {
        "name": 'Huyện Càng Long',
        "value": 'Huyện Càng Long',
        "parent": 'Tỉnh Trà Vinh'
    },
    {
        "name": 'Huyện Cầu Kè',
        "value": 'Huyện Cầu Kè',
        "parent": 'Tỉnh Trà Vinh'
    },
    {
        "name": 'Huyện Tiểu Cần',
        "value": 'Huyện Tiểu Cần',
        "parent": 'Tỉnh Trà Vinh'
    },
    {
        "name": 'Huyện Châu Thành',
        "value": 'Huyện Châu Thành',
        "parent": 'Tỉnh Trà Vinh'
    },
    {
        "name": 'Huyện Cầu Ngang',
        "value": 'Huyện Cầu Ngang',
        "parent": 'Tỉnh Trà Vinh'
    },
    {
        "name": 'Huyện Trà Cú',
        "value": 'Huyện Trà Cú',
        "parent": 'Tỉnh Trà Vinh'
    },
    {
        "name": 'Huyện Duyên Hải',
        "value": 'Huyện Duyên Hải',
        "parent": 'Tỉnh Trà Vinh'
    },
    {
        "name": 'Thị xã Duyên Hải',
        "value": 'Thị xã Duyên Hải',
        "parent": 'Tỉnh Trà Vinh'
    },
    {
        "name": 'Thành phố Vĩnh Long',
        "value": 'Thành phố Vĩnh Long',
        "parent": 'Tỉnh Vĩnh Long'
    },
    {
        "name": 'Huyện Long Hồ',
        "value": 'Huyện Long Hồ',
        "parent": 'Tỉnh Vĩnh Long'
    },
    {
        "name": 'Huyện Mang Thít',
        "value": 'Huyện Mang Thít',
        "parent": 'Tỉnh Vĩnh Long'
    },
    {
        "name": 'Huyện Vũng Liêm',
        "value": 'Huyện Vũng Liêm',
        "parent": 'Tỉnh Vĩnh Long'
    },
    {
        "name": 'Huyện Tam Bình',
        "value": 'Huyện Tam Bình',
        "parent": 'Tỉnh Vĩnh Long'
    },
    {
        "name": 'Thị xã Bình Minh',
        "value": 'Thị xã Bình Minh',
        "parent": 'Tỉnh Vĩnh Long'
    },
    {
        "name": 'Huyện Trà Ôn',
        "value": 'Huyện Trà Ôn',
        "parent": 'Tỉnh Vĩnh Long'
    },
    {
        "name": 'Huyện Bình Tân',
        "value": 'Huyện Bình Tân',
        "parent": 'Tỉnh Vĩnh Long'
    },
    {
        "name": 'Thành phố Cao Lãnh',
        "value": 'Thành phố Cao Lãnh',
        "parent": 'Tỉnh Đồng Tháp'
    },
    {
        "name": 'Thành phố Sa Đéc',
        "value": 'Thành phố Sa Đéc',
        "parent": 'Tỉnh Đồng Tháp'
    },
    {
        "name": 'Thị xã Hồng Ngự',
        "value": 'Thị xã Hồng Ngự',
        "parent": 'Tỉnh Đồng Tháp'
    },
    {
        "name": 'Huyện Tân Hồng',
        "value": 'Huyện Tân Hồng',
        "parent": 'Tỉnh Đồng Tháp'
    },
    {
        "name": 'Huyện Hồng Ngự',
        "value": 'Huyện Hồng Ngự',
        "parent": 'Tỉnh Đồng Tháp'
    },
    {
        "name": 'Huyện Tam Nông',
        "value": 'Huyện Tam Nông',
        "parent": 'Tỉnh Đồng Tháp'
    },
    {
        "name": 'Huyện Tháp Mười',
        "value": 'Huyện Tháp Mười',
        "parent": 'Tỉnh Đồng Tháp'
    },
    {
        "name": 'Huyện Cao Lãnh',
        "value": 'Huyện Cao Lãnh',
        "parent": 'Tỉnh Đồng Tháp'
    },
    {
        "name": 'Huyện Thanh Bình',
        "value": 'Huyện Thanh Bình',
        "parent": 'Tỉnh Đồng Tháp'
    },
    {
        "name": 'Huyện Lấp Vò',
        "value": 'Huyện Lấp Vò',
        "parent": 'Tỉnh Đồng Tháp'
    },
    {
        "name": 'Huyện Lai Vung',
        "value": 'Huyện Lai Vung',
        "parent": 'Tỉnh Đồng Tháp'
    },
    {
        "name": 'Huyện Châu Thành',
        "value": 'Huyện Châu Thành',
        "parent": 'Tỉnh Đồng Tháp'
    },
    {
        "name": 'Thành phố Long Xuyên',
        "value": 'Thành phố Long Xuyên',
        "parent": 'Tỉnh An Giang'
    },
    {
        "name": 'Thành phố Châu Đốc',
        "value": 'Thành phố Châu Đốc',
        "parent": 'Tỉnh An Giang'
    },
    {
        "name": 'Huyện An Phú',
        "value": 'Huyện An Phú',
        "parent": 'Tỉnh An Giang'
    },
    {
        "name": 'Thị xã Tân Châu',
        "value": 'Thị xã Tân Châu',
        "parent": 'Tỉnh An Giang'
    },
    {
        "name": 'Huyện Phú Tân',
        "value": 'Huyện Phú Tân',
        "parent": 'Tỉnh An Giang'
    },
    {
        "name": 'Huyện Châu Phú',
        "value": 'Huyện Châu Phú',
        "parent": 'Tỉnh An Giang'
    },
    {
        "name": 'Huyện Tịnh Biên',
        "value": 'Huyện Tịnh Biên',
        "parent": 'Tỉnh An Giang'
    },
    {
        "name": 'Huyện Tri Tôn',
        "value": 'Huyện Tri Tôn',
        "parent": 'Tỉnh An Giang'
    },
    {
        "name": 'Huyện Châu Thành',
        "value": 'Huyện Châu Thành',
        "parent": 'Tỉnh An Giang'
    },
    {
        "name": 'Huyện Chợ Mới',
        "value": 'Huyện Chợ Mới',
        "parent": 'Tỉnh An Giang'
    },
    {
        "name": 'Huyện Thoại Sơn',
        "value": 'Huyện Thoại Sơn',
        "parent": 'Tỉnh An Giang'
    },
    {
        "name": 'Thành phố Rạch Giá',
        "value": 'Thành phố Rạch Giá',
        "parent": 'Tỉnh Kiên Giang'
    },
    {
        "name": 'Thành phố Hà Tiên',
        "value": 'Thành phố Hà Tiên',
        "parent": 'Tỉnh Kiên Giang'
    },
    {
        "name": 'Huyện Kiên Lương',
        "value": 'Huyện Kiên Lương',
        "parent": 'Tỉnh Kiên Giang'
    },
    {
        "name": 'Huyện Hòn Đất',
        "value": 'Huyện Hòn Đất',
        "parent": 'Tỉnh Kiên Giang'
    },
    {
        "name": 'Huyện Tân Hiệp',
        "value": 'Huyện Tân Hiệp',
        "parent": 'Tỉnh Kiên Giang'
    },
    {
        "name": 'Huyện Châu Thành',
        "value": 'Huyện Châu Thành',
        "parent": 'Tỉnh Kiên Giang'
    },
    {
        "name": 'Huyện Giồng Riềng',
        "value": 'Huyện Giồng Riềng',
        "parent": 'Tỉnh Kiên Giang'
    },
    {
        "name": 'Huyện Gò Quao',
        "value": 'Huyện Gò Quao',
        "parent": 'Tỉnh Kiên Giang'
    },
    {
        "name": 'Huyện An Biên',
        "value": 'Huyện An Biên',
        "parent": 'Tỉnh Kiên Giang'
    },
    {
        "name": 'Huyện An Minh',
        "value": 'Huyện An Minh',
        "parent": 'Tỉnh Kiên Giang'
    },
    {
        "name": 'Huyện Vĩnh Thuận',
        "value": 'Huyện Vĩnh Thuận',
        "parent": 'Tỉnh Kiên Giang'
    },
    {
        "name": 'Huyện Phú Quốc',
        "value": 'Huyện Phú Quốc',
        "parent": 'Tỉnh Kiên Giang'
    },
    {
        "name": 'Huyện Kiên Hải',
        "value": 'Huyện Kiên Hải',
        "parent": 'Tỉnh Kiên Giang'
    },
    {
        "name": 'Huyện U Minh Thượng',
        "value": 'Huyện U Minh Thượng',
        "parent": 'Tỉnh Kiên Giang'
    },
    {
        "name": 'Huyện Giang Thành',
        "value": 'Huyện Giang Thành',
        "parent": 'Tỉnh Kiên Giang'
    },
    {
        "name": 'Quận Ninh Kiều',
        "value": 'Quận Ninh Kiều',
        "parent": 'Thành phố Cần Thơ'
    },
    {
        "name": 'Quận Ô Môn',
        "value": 'Quận Ô Môn',
        "parent": 'Thành phố Cần Thơ'
    },
    {
        "name": 'Quận Bình Thuỷ',
        "value": 'Quận Bình Thuỷ',
        "parent": 'Thành phố Cần Thơ'
    },
    {
        "name": 'Quận Cái Răng',
        "value": 'Quận Cái Răng',
        "parent": 'Thành phố Cần Thơ'
    },
    {
        "name": 'Quận Thốt Nốt',
        "value": 'Quận Thốt Nốt',
        "parent": 'Thành phố Cần Thơ'
    },
    {
        "name": 'Huyện Vĩnh Thạnh',
        "value": 'Huyện Vĩnh Thạnh',
        "parent": 'Thành phố Cần Thơ'
    },
    {
        "name": 'Huyện Cờ Đỏ',
        "value": 'Huyện Cờ Đỏ',
        "parent": 'Thành phố Cần Thơ'
    },
    {
        "name": 'Huyện Phong Điền',
        "value": 'Huyện Phong Điền',
        "parent": 'Thành phố Cần Thơ'
    },
    {
        "name": 'Huyện Thới Lai',
        "value": 'Huyện Thới Lai',
        "parent": 'Thành phố Cần Thơ'
    },
    {
        "name": 'Thành phố Vị Thanh',
        "value": 'Thành phố Vị Thanh',
        "parent": 'Tỉnh Hậu Giang'
    },
    {
        "name": 'Thành phố Ngã Bảy',
        "value": 'Thành phố Ngã Bảy',
        "parent": 'Tỉnh Hậu Giang'
    },
    {
        "name": 'Huyện Châu Thành A',
        "value": 'Huyện Châu Thành A',
        "parent": 'Tỉnh Hậu Giang'
    },
    {
        "name": 'Huyện Châu Thành',
        "value": 'Huyện Châu Thành',
        "parent": 'Tỉnh Hậu Giang'
    },
    {
        "name": 'Huyện Phụng Hiệp',
        "value": 'Huyện Phụng Hiệp',
        "parent": 'Tỉnh Hậu Giang'
    },
    {
        "name": 'Huyện Vị Thuỷ',
        "value": 'Huyện Vị Thuỷ',
        "parent": 'Tỉnh Hậu Giang'
    },
    {
        "name": 'Huyện Long Mỹ',
        "value": 'Huyện Long Mỹ',
        "parent": 'Tỉnh Hậu Giang'
    },
    {
        "name": 'Thị xã Long Mỹ',
        "value": 'Thị xã Long Mỹ',
        "parent": 'Tỉnh Hậu Giang'
    },
    {
        "name": 'Thành phố Sóc Trăng',
        "value": 'Thành phố Sóc Trăng',
        "parent": 'Tỉnh Sóc Trăng'
    },
    {
        "name": 'Huyện Châu Thành',
        "value": 'Huyện Châu Thành',
        "parent": 'Tỉnh Sóc Trăng'
    },
    {
        "name": 'Huyện Kế Sách',
        "value": 'Huyện Kế Sách',
        "parent": 'Tỉnh Sóc Trăng'
    },
    {
        "name": 'Huyện Mỹ Tú',
        "value": 'Huyện Mỹ Tú',
        "parent": 'Tỉnh Sóc Trăng'
    },
    {
        "name": 'Huyện Cù Lao Dung',
        "value": 'Huyện Cù Lao Dung',
        "parent": 'Tỉnh Sóc Trăng'
    },
    {
        "name": 'Huyện Long Phú',
        "value": 'Huyện Long Phú',
        "parent": 'Tỉnh Sóc Trăng'
    },
    {
        "name": 'Huyện Mỹ Xuyên',
        "value": 'Huyện Mỹ Xuyên',
        "parent": 'Tỉnh Sóc Trăng'
    },
    {
        "name": 'Thị xã Ngã Năm',
        "value": 'Thị xã Ngã Năm',
        "parent": 'Tỉnh Sóc Trăng'
    },
    {
        "name": 'Huyện Thạnh Trị',
        "value": 'Huyện Thạnh Trị',
        "parent": 'Tỉnh Sóc Trăng'
    },
    {
        "name": 'Thị xã Vĩnh Châu',
        "value": 'Thị xã Vĩnh Châu',
        "parent": 'Tỉnh Sóc Trăng'
    },
    {
        "name": 'Huyện Trần Đề',
        "value": 'Huyện Trần Đề',
        "parent": 'Tỉnh Sóc Trăng'
    },
    {
        "name": 'Thành phố Bạc Liêu',
        "value": 'Thành phố Bạc Liêu',
        "parent": 'Tỉnh Bạc Liêu'
    },
    {
        "name": 'Huyện Hồng Dân',
        "value": 'Huyện Hồng Dân',
        "parent": 'Tỉnh Bạc Liêu'
    },
    {
        "name": 'Huyện Phước Long',
        "value": 'Huyện Phước Long',
        "parent": 'Tỉnh Bạc Liêu'
    },
    {
        "name": 'Huyện Vĩnh Lợi',
        "value": 'Huyện Vĩnh Lợi',
        "parent": 'Tỉnh Bạc Liêu'
    },
    {
        "name": 'Thị xã Giá Rai',
        "value": 'Thị xã Giá Rai',
        "parent": 'Tỉnh Bạc Liêu'
    },
    {
        "name": 'Huyện Đông Hải',
        "value": 'Huyện Đông Hải',
        "parent": 'Tỉnh Bạc Liêu'
    },
    {
        "name": 'Huyện Hoà Bình',
        "value": 'Huyện Hoà Bình',
        "parent": 'Tỉnh Bạc Liêu'
    },
    {
        "name": 'Thành phố Cà Mau',
        "value": 'Thành phố Cà Mau',
        "parent": 'Tỉnh Cà Mau'
    },
    {
        "name": 'Huyện U Minh',
        "value": 'Huyện U Minh',
        "parent": 'Tỉnh Cà Mau'
    },
    {
        "name": 'Huyện Thới Bình',
        "value": 'Huyện Thới Bình',
        "parent": 'Tỉnh Cà Mau'
    },
    {
        "name": 'Huyện Trần Văn Thời',
        "value": 'Huyện Trần Văn Thời',
        "parent": 'Tỉnh Cà Mau'
    },
    {
        "name": 'Huyện Cái Nước',
        "value": 'Huyện Cái Nước',
        "parent": 'Tỉnh Cà Mau'
    },
    {
        "name": 'Huyện Đầm Dơi',
        "value": 'Huyện Đầm Dơi',
        "parent": 'Tỉnh Cà Mau'
    },
    {
        "name": 'Huyện Năm Căn',
        "value": 'Huyện Năm Căn',
        "parent": 'Tỉnh Cà Mau'
    },
    {
        "name": 'Huyện Phú Tân',
        "value": 'Huyện Phú Tân',
        "parent": 'Tỉnh Cà Mau'
    },
    {
        "name": 'Huyện Ngọc Hiển',
        "value": 'Huyện Ngọc Hiển',
        "parent": 'Tỉnh Cà Mau'
    },
    {
        "name": 'Huyện Tĩnh Gia',
        "value": 'Huyện Tĩnh Gia',
        "parent": 'Tỉnh Thanh Hóa'
    }
]

PROVINCES = [
    {
        "name": 'Thành phố Hà Nội',
        "value": 'Thành phố Hà Nội'
    },
    {
        "name": 'Tỉnh Hà Giang',
        "value": 'Tỉnh Hà Giang'
    },
    {
        "name": 'Tỉnh Cao Bằng',
        "value": 'Tỉnh Cao Bằng'
    },
    {
        "name": 'Tỉnh Bắc Kạn',
        "value": 'Tỉnh Bắc Kạn'
    },
    {
        "name": 'Tỉnh Tuyên Quang',
        "value": 'Tỉnh Tuyên Quang'
    },
    {
        "name": 'Tỉnh Lào Cai',
        "value": 'Tỉnh Lào Cai'
    },
    {
        "name": 'Tỉnh Điện Biên',
        "value": 'Tỉnh Điện Biên'
    },
    {
        "name": 'Tỉnh Lai Châu',
        "value": 'Tỉnh Lai Châu'
    },
    {
        "name": 'Tỉnh Sơn La',
        "value": 'Tỉnh Sơn La'
    },
    {
        "name": 'Tỉnh Yên Bái',
        "value": 'Tỉnh Yên Bái'
    },
    {
        "name": 'Tỉnh Hòa Bình',
        "value": 'Tỉnh Hòa Bình'
    },
    {
        "name": 'Tỉnh Thái Nguyên',
        "value": 'Tỉnh Thái Nguyên'
    },
    {
        "name": 'Tỉnh Lạng Sơn',
        "value": 'Tỉnh Lạng Sơn'
    },
    {
        "name": 'Tỉnh Quảng Ninh',
        "value": 'Tỉnh Quảng Ninh'
    },
    {
        "name": 'Tỉnh Bắc Giang',
        "value": 'Tỉnh Bắc Giang'
    },
    {
        "name": 'Tỉnh Phú Thọ',
        "value": 'Tỉnh Phú Thọ'
    },
    {
        "name": 'Tỉnh Vĩnh Phúc',
        "value": 'Tỉnh Vĩnh Phúc'
    },
    {
        "name": 'Tỉnh Bắc Ninh',
        "value": 'Tỉnh Bắc Ninh'
    },
    {
        "name": 'Tỉnh Hải Dương',
        "value": 'Tỉnh Hải Dương'
    },
    {
        "name": 'Thành phố Hải Phòng',
        "value": 'Thành phố Hải Phòng'
    },
    {
        "name": 'Tỉnh Hưng Yên',
        "value": 'Tỉnh Hưng Yên'
    },
    {
        "name": 'Tỉnh Thái Bình',
        "value": 'Tỉnh Thái Bình'
    },
    {
        "name": 'Tỉnh Hà Nam',
        "value": 'Tỉnh Hà Nam'
    },
    {
        "name": 'Tỉnh Nam Định',
        "value": 'Tỉnh Nam Định'
    },
    {
        "name": 'Tỉnh Ninh Bình',
        "value": 'Tỉnh Ninh Bình'
    },
    {
        "name": 'Tỉnh Thanh Hóa',
        "value": 'Tỉnh Thanh Hóa'
    },
    {
        "name": 'Tỉnh Nghệ An',
        "value": 'Tỉnh Nghệ An'
    },
    {
        "name": 'Tỉnh Hà Tĩnh',
        "value": 'Tỉnh Hà Tĩnh'
    },
    {
        "name": 'Tỉnh Quảng Bình',
        "value": 'Tỉnh Quảng Bình'
    },
    {
        "name": 'Tỉnh Quảng Trị',
        "value": 'Tỉnh Quảng Trị'
    },
    {
        "name": 'Tỉnh Thừa Thiên Huế',
        "value": 'Tỉnh Thừa Thiên Huế'
    },
    {
        "name": 'Thành phố Đà Nẵng',
        "value": 'Thành phố Đà Nẵng'
    },
    {
        "name": 'Tỉnh Quảng Nam',
        "value": 'Tỉnh Quảng Nam'
    },
    {
        "name": 'Tỉnh Quảng Ngãi',
        "value": 'Tỉnh Quảng Ngãi'
    },
    {
        "name": 'Tỉnh Bình Định',
        "value": 'Tỉnh Bình Định'
    },
    {
        "name": 'Tỉnh Phú Yên',
        "value": 'Tỉnh Phú Yên'
    },
    {
        "name": 'Tỉnh Khánh Hòa',
        "value": 'Tỉnh Khánh Hòa'
    },
    {
        "name": 'Tỉnh Ninh Thuận',
        "value": 'Tỉnh Ninh Thuận'
    },
    {
        "name": 'Tỉnh Bình Thuận',
        "value": 'Tỉnh Bình Thuận'
    },
    {
        "name": 'Tỉnh Kon Tum',
        "value": 'Tỉnh Kon Tum'
    },
    {
        "name": 'Tỉnh Gia Lai',
        "value": 'Tỉnh Gia Lai'
    },
    {
        "name": 'Tỉnh Đắk Lắk',
        "value": 'Tỉnh Đắk Lắk'
    },
    {
        "name": 'Tỉnh Đắk Nông',
        "value": 'Tỉnh Đắk Nông'
    },
    {
        "name": 'Tỉnh Lâm Đồng',
        "value": 'Tỉnh Lâm Đồng'
    },
    {
        "name": 'Tỉnh Bình Phước',
        "value": 'Tỉnh Bình Phước'
    },
    {
        "name": 'Tỉnh Tây Ninh',
        "value": 'Tỉnh Tây Ninh'
    },
    {
        "name": 'Tỉnh Bình Dương',
        "value": 'Tỉnh Bình Dương'
    },
    {
        "name": 'Tỉnh Đồng Nai',
        "value": 'Tỉnh Đồng Nai'
    },
    {
        "name": 'Tỉnh Bà Rịa - Vũng Tàu',
        "value": 'Tỉnh Bà Rịa - Vũng Tàu'
    },
    {
        "name": 'Thành phố Hồ Chí Minh',
        "value": 'Thành phố Hồ Chí Minh'
    },
    {
        "name": 'Tỉnh Long An',
        "value": 'Tỉnh Long An'
    },
    {
        "name": 'Tỉnh Tiền Giang',
        "value": 'Tỉnh Tiền Giang'
    },
    {
        "name": 'Tỉnh Bến Tre',
        "value": 'Tỉnh Bến Tre'
    },
    {
        "name": 'Tỉnh Trà Vinh',
        "value": 'Tỉnh Trà Vinh'
    },
    {
        "name": 'Tỉnh Vĩnh Long',
        "value": 'Tỉnh Vĩnh Long'
    },
    {
        "name": 'Tỉnh Đồng Tháp',
        "value": 'Tỉnh Đồng Tháp'
    },
    {
        "name": 'Tỉnh An Giang',
        "value": 'Tỉnh An Giang'
    },
    {
        "name": 'Tỉnh Kiên Giang',
        "value": 'Tỉnh Kiên Giang'
    },
    {
        "name": 'Thành phố Cần Thơ',
        "value": 'Thành phố Cần Thơ'
    },
    {
        "name": 'Tỉnh Hậu Giang',
        "value": 'Tỉnh Hậu Giang'
    },
    {
        "name": 'Tỉnh Sóc Trăng',
        "value": 'Tỉnh Sóc Trăng'
    },
    {
        "name": 'Tỉnh Bạc Liêu',
        "value": 'Tỉnh Bạc Liêu'
    },
    {
        "name": 'Tỉnh Cà Mau',
        "value": 'Tỉnh Cà Mau'
    }
]

def get_context(context):
    context.no_cache = True
    args = frappe.request.args
    lang = args.get('lang', 'vi')
    context.lang = lang
    context.districts = DISTRICTS
    context.provinces = PROVINCES
    key = frappe.form_dict.key
    context.billing_info = {
        "billing_name": "",
        "email_id": "",
        "phone": "",
    }
    try:
        account_request = get_account_request_from_key(key)
        if account_request:
            context.billing_info = {
                "billing_name": account_request.first_name or "",
                "email_id": account_request.email or "",
                "phone": account_request.phone_number or "",
            }
    except:
        pass
    return context
