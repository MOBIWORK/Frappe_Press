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
				title: this.$t('Logging_in_as_Administrator'),
				message: `${this.$t('Please_wait')}...`,
				icon: 'alert-circle',
				color: 'yellow'
			});
		},
		onError(err) {
			notify({
				title: this.$t('Unable_to_log_in_as_Administrator'),
				message: err.messages.join('\n'),
				color: 'red',
				icon: 'x'
			});
		}
	};
}
