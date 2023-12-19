import { notify } from '@/utils/toast';

export function loginAsAdmin(siteName) {
	return {
		url: 'press.api.site.login',
		params: { name: siteName },
		onSuccess(data) {
			if (data?.sid && data?.site) {
				window.open(`https://${data.site}/desk?sid=${data.sid}`, '_blank');
			}
		},
		validate() {
			// hack to display the toast
			notify({
				title: 'Đang cố gắng đăng nhập với tư cách Quản trị viên',
				message: `Vui lòng đợi...`,
				icon: 'alert-circle',
				color: 'yellow'
			});
		},
		onError(err) {
			notify({
				title: 'Không thể đăng nhập với tư cách Quản trị viên',
				message: err.messages.join('\n'),
				color: 'red',
				icon: 'x'
			});
		}
	};
}
