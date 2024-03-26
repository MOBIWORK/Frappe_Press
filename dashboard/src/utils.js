import { DateTime, Duration } from 'luxon';
import theme from '../tailwind.theme.json';

let utils = {
	methods: {
		$translateMessage(key) {
			if (key) {
				if (Array.isArray(key)) {
					let msg = '';
					key.map(el => {
						msg += this.$t(el);
					});
				} else {
					return this.$t(key);
				}
			}

			return '';
		},
		$validdateInput(val, type) {
			let emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
			let msgError = '';
			switch (type) {
				case 'email':
					// code block
					if (!val) {
						msgError = 'utils_content_11';
						break;
					}
					if (!emailRegex.test(val)) {
						msgError = 'utils_content_13';
					}
					break;
				case 'password':
					if (!val) {
						msgError = 'utils_content_12';
					}
					// code block
					break;
				default:
				// code block
			}
			return [msgError ? 1 : 0, msgError];
		},
		$validateSubdomain(subdomain) {
			if (!subdomain) {
				return this.$t('Subdomain_cannot_be_empty');
			}
			if (subdomain.length < 2) {
				return this.$t('utils_content_1');
			}
			if (subdomain.length > 32) {
				return this.$t('utils_content_2');
			}
			if (!subdomain.match(/^[a-z0-9][a-z0-9-]*[a-z0-9]$/)) {
				return this.$t('utils_content_3');
			}
			return null;
		},
		$plural(number, singular, plural) {
			if (number === 1) {
				return singular;
			}
			return plural;
		},
		$date(date, serverDatesTimezone = 'Asia/Ho_Chi_Minh') {
			// assuming all dates on the server are stored in our timezone

			let localZone = DateTime.local().zoneName;
			return DateTime.fromSQL(date, { zone: serverDatesTimezone }).setZone(
				localZone
			);
		},
		round(number, precision) {
			let multiplier = Math.pow(10, precision || 0);
			return Math.round(number * multiplier) / multiplier;
		},
		formatDate(value, type = 'DATETIME_FULL', isUTC = false) {
			let datetime = isUTC ? this.$date(value, 'UTC') : this.$date(value);
			let format = value;
			if (type === 'relative') {
				format = datetime.toRelative();
			} else {
				let formatOptions = DateTime[type];
				format = datetime.toLocaleString(formatOptions);
			}
			return format;
		},
		$formatDate(d) {
			return this.$date(d).toFormat('dd-MM-yyyy');
		},
		$getFormatTimeNow(f) {
			return DateTime.now().toFormat(f, { zone: 'Asia/Ho_Chi_Minh' });
		},
		$getDays(year, month) {
			return new Date(year, month, 0).getDate();
		},
		$formatDateDetail(d) {
			return this.$date(d).toFormat('dd-MM-yyyy hh:mm:ss');
		},
		$formatTitleJob(value) {
			let nameTitle = {
				'New Site': this.$t('utils_content_4'),
				'Install Apps': this.$t('utils_content_5'),
				'Update Site Configuration': this.$t('utils_content_6'),
				'Enable Scheduler': this.$t('utils_content_7'),
				'Bench Setup NGINX': this.$t('utils_content_8'),
				'Reload NGINX': this.$t('utils_content_9')
			};
			return nameTitle[value] || value;
		},
		$formatDuration(value) {
			// Remove decimal seconds
			value = value.split('.')[0];

			// Add leading zero
			// 0:0:2 -> 00:00:02
			const formattedDuration = value
				.split(':')
				.map(x => x.padStart(2, '0'))
				.join(':');

			const dateTime = Duration.fromISOTime(formattedDuration).toObject();
			const hourString = dateTime.hours
				? `${dateTime.hours} ${this.$t('hour')}`
				: '';
			const minuteString = dateTime.minutes
				? `${dateTime.minutes} ${this.$t('minute')}`
				: '';
			const secondString = `${dateTime.seconds} ${this.$t('second')}`;

			return `${hourString} ${minuteString} ${secondString}`;
		},
		formatBytes(bytes, decimals = 2, current = 0) {
			if (bytes === 0) return '0 Bytes';

			const k = 1024;
			const dm = decimals < 0 ? 0 : decimals;
			const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
			const i = Math.floor(Math.log(Math.abs(bytes)) / Math.log(k));

			return (
				parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) +
				' ' +
				sizes[i + current]
			);
		},
		$formatCPUTime(duration) {
			return duration / 1000000;
		},
		$formatMoney(price, precision = 2) {
			price = this.round(price, precision) || price;
			return price?.toLocaleString('da-DK') || price;
		},
		$planTitle(plan) {
			let price_field = 'price_vnd';
			let currency = 'VND';
			let price =
				plan.block_monthly == 1 ? plan[price_field] * 12 : plan[price_field];
			let price_string = this.$formatMoney(price);
			let display_price = `${price_string} ${currency}`;
			return price > 0 ? `${display_price}` : plan.plan_title;
		},
		trialEndsInDaysText(date) {
			let diff = this.$date(date).diff(DateTime.local(), ['days']).toObject();

			let days = diff.days;
			if (days > 1) {
				return `${this.$t('in')} ${Math.floor(days)} ${this.$t('days')}`;
			}
			return this.$t('utils_content_10');
		},
		$routeTo404PageIfNotFound(errorMessage) {
			if (errorMessage.indexOf('not found') >= 0) {
				this.$router.push({
					name: 'NotFound',
					// preserve current path and remove the first char to avoid the target URL starting with `//`
					params: { pathMatch: this.$route.path.substring(1).split('/') },
					// preserve existing query and hash if any
					query: this.$route.query,
					hash: this.$route.hash
				});
			}
		},
		$getStatusDocTrans(t) {
			let statusDoc = {
				0: this.$t('unpaid'),
				1: this.$t('paid'),
				2: this.$t('cancelled'),
				3: this.$t('processing')
			};
			return statusDoc[t] || t;
		},
		$getTypeSource(t) {
			let typeSource = {
				'Prepaid Credits': this.$t('deposit_amount'),
				'Transferred Credits': this.$t('transferred_amount'),
				'Free Credits': this.$t('promotional_amount')
			};
			return typeSource[t] || t;
		},
		$invoiceStatus(status) {
			let objStatus = {
				Paid: this.$t('paid'),
				Unpaid: this.$t('unpaid'),
				'Invoice Created': this.$t('invoice_created')
			};
			return objStatus[status] || status;
		},
		$jobStatus(status) {
			let objStatus = {
				Active: this.$t('active'),
				Undelivered: this.$t('Undelivered'),
				Pending: this.$t('Pending'),
				Running: this.$t('Running'),
				Success: this.$t('Success'),
				Failure: this.$t('Failure'),
				'Awaiting Deploy': this.$t('Awaiting_Deploy')
			};
			return objStatus[status] || status;
		},
		$siteStatus(site) {
			let statusSite = {
				Active: this.$t('active'),
				Pending: this.$t('pending'),
				Installing: this.$t('installing'),
				Updating: this.$t('updating'),
				Inactive: this.$t('inactive'),
				Broken: this.$t('broken'),
				Archived: this.$t('archived'),
				Suspended: this.$t('suspended')
			};
			let status = statusSite[site.status] || site.status;

			if (site.update_available && site.status == 'Active') {
				status = this.$t('Updates_available');
			}

			let usage = Math.max(
				site.current_cpu_usage,
				site.current_database_usage,
				site.current_disk_usage
			);
			if (usage && usage >= 80 && status == 'Active') {
				status = this.$t('Note');
			}
			if (site.trial_end_date) {
				status = this.$t('Trial');
			}
			return status;
		}
	},
	computed: {
		$theme() {
			return theme;
		},
		$platform() {
			const ua = navigator.userAgent.toLowerCase();

			if (ua.indexOf('win') > -1) {
				return 'win';
			} else if (ua.indexOf('mac') > -1) {
				return 'mac';
			} else if (ua.indexOf('x11') > -1 || ua.indexOf('linux') > -1) {
				return 'linux';
			}
		}
	}
};

export function validateGST(gst) {
	// https://github.com/raysk4ever/raysk-vali/blob/master/validate.js#L51
	const gstReg = new RegExp(
		/\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1}/
	);
	return gstReg.test(gst);
}

export default function install(Vue) {
	Vue.mixin(utils);
}

export function isWasmSupported() {
	// Check if browser supports WASM
	// ref: https://stackoverflow.com/a/47880734/10309266
	return (() => {
		try {
			if (
				typeof WebAssembly === 'object' &&
				typeof WebAssembly.instantiate === 'function'
			) {
				const module = new WebAssembly.Module(
					Uint8Array.of(0x0, 0x61, 0x73, 0x6d, 0x01, 0x00, 0x00, 0x00)
				);
				if (module instanceof WebAssembly.Module)
					return (
						new WebAssembly.Instance(module) instanceof WebAssembly.Instance
					);
			}
		} catch (e) {} // eslint-disable-line no-empty
		return false;
	})();
}

export async function trypromise(promise) {
	try {
		let data = await promise;
		return [null, data];
	} catch (error) {
		return [error, null];
	}
}

export { utils };
export { default as dayjs } from './utils/dayjs';
