<template>
	<FrappeUIBadge :label="label" :theme="color" />
</template>

<script>
import { Badge as FrappeUIBadge } from 'frappe-ui';

export default {
	name: 'Badge',
	props: ['label'],
	components: {
		FrappeUIBadge
	},
	computed: {
		color() {
			return {
				'Đã thanh toán': 'green',
				'Chưa thanh toán': 'orange',
				'Hoạt động': 'green',
				'Đang xử lý': 'orange',
				'Đang cài đặt': 'orange',
				'Đang cập nhật': 'gray',
				'Dừng hoạt động': 'gray',
				'Đang chạy': 'green',
				'Thành công': 'green',
				'Thât bại': 'red',
				Lỗi: 'red',
				'Đã lưu trữ': 'gray',
				Approved: 'green',
				Broken: 'red',
				Installing: 'orange',
				Running: 'green',
				Pending: 'orange',
				Failure: 'red',
				'Update Available': 'blue',
				Enabled: 'blue',
				'Awaiting Approval': 'orange',
				[this.$t('Awaiting_Deploy')]: 'orange',
				Success: 'green',
				Deployed: 'green',
				Expired: 'red',
				Paid: 'green',
				Unpaid: 'orange',
				'Invoice Created': 'blue',
				'Đã tạo hóa đơn': 'blue',
				Rejected: 'red',
				'In Review': 'orange',
				'Attention Required': 'red',
				Active: 'green',
				Trial: 'orange',
				Published: 'green',
				Owner: 'blue',
				Primary: 'green',
				'Latest Deployed': 'orange'
			}[this.label];
		}
	}
};
</script>
