import { DateTime, Duration } from 'luxon';
import theme from '../tailwind.theme.json';

let utils = {
	methods: {
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
		$formatDateDetail(d) {
			return this.$date(d).toFormat('dd-MM-yyyy hh:mm:ss');
		},
		$formatTitleJob(value) {
			let nameTitle = {
				'New Site': 'Tạo tổ chức',
				'Install Apps': 'Cài đặt app',
				'Update Site Configuration': 'Cấu hình hệ thống',
				'Enable Scheduler': 'Bật trình lập lịch',
				'Bench Setup NGINX': 'Khởi tạo tên miền',
				'Reload NGINX': 'Hoàn thành'
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
			const hourString = dateTime.hours ? `${dateTime.hours} giờ` : '';
			const minuteString = dateTime.minutes ? `${dateTime.minutes} phút` : '';
			const secondString = `${dateTime.seconds} giây`;

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
		$formatMoney(price) {
			const VND = new Intl.NumberFormat('vi-VN', {
				style: 'currency',
				currency: 'VND'
			});

			return VND.format(price).split('₫')[0].trim();
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
				return `in ${Math.floor(days)} days`;
			}
			return 'in a day';
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
		$siteStatus(site) {
			let statusSite = {
				Active: 'Hoạt động',
				Pending: 'Đang xử lý',
				Installing: 'Đang cài đặt',
				Updating: 'Đang cập nhật',
				Inactive: 'Dừng hoạt động',
				Broken: 'Lỗi',
				Archived: 'Đã lưu trữ',
				Suspended: 'Đình chỉ'
			};
			let status = statusSite[site.status] || site.status;

			if (site.update_available && site.status == 'Active') {
				status = 'Cập nhật có sẵn';
			}

			let usage = Math.max(
				site.current_cpu_usage,
				site.current_database_usage,
				site.current_disk_usage
			);
			if (usage && usage >= 80 && status == 'Active') {
				status = 'Chú ý';
			}
			if (site.trial_end_date) {
				status = 'Dùng thử';
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

export function validateSubdomain(subdomain) {
	if (!subdomain) {
		return 'Tên miền không thể trống.';
	}
	if (subdomain.length < 5) {
		return 'Tên miền quá ngắn. Hãy sử dụng 5 ký tự trở lên.';
	}
	if (subdomain.length > 32) {
		return 'Tên miền quá dài. Sử dụng 32 ký tự trở xuống';
	}
	if (!subdomain.match(/^[a-z0-9][a-z0-9-]*[a-z0-9]$/)) {
		return 'Tên miền chứa các ký tự không hợp lệ. Sử dụng ký tự chữ thường, số và dấu gạch nối';
	}
	return null;
}

export { utils };
export { default as dayjs } from './utils/dayjs';
