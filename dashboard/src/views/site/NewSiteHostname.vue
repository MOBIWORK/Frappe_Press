<template>
	<div>
		<label class="text-lg font-semibold"> Chọn một tên miền </label>
		<p class="text-base text-gray-700">
			Đặt tên cho tổ chức của bạn. Chỉ có thể chứa các ký tự chữ và số cũng như
			dấu gạch ngang.
		</p>
		<div class="mt-4 flex">
			<input
				class="form-input z-10 w-full rounded-r-none"
				type="text"
				:value="modelValue"
				placeholder="subdomain"
				@change="subdomainChange"
			/>
			<div class="flex items-center rounded-r bg-gray-100 px-4 text-base">
				.{{ domain }}
			</div>
		</div>
		<div class="mt-1">
			<div
				v-if="subdomainAvailable"
				class="text-sm text-green-600"
				role="alert"
			>
				{{ modelValue }}.{{ domain }} hợp lệ
			</div>
			<ErrorMessage :message="errorMessage" />
		</div>
		<div class="mt-4">
			<div>
				<input
					id="checkrestore"
					name="checkrestore"
					label="ok"
					type="radio"
					class="form-radio text-gray-900"
					:checked="true"
					value="new"
					@change="checkRestoreChange"
				/>
				<label class="ml-2 text-base" for="checkrestore">Tạo mới dữ liệu</label>
			</div>
			<div class="mt-2">
				<input
					id="checkrestore1"
					name="checkrestore"
					label="ok"
					type="radio"
					value="restore"
					class="form-radio text-gray-900"
					@change="checkRestoreChange"
				/>
				<label class="ml-2 text-base" for="checkrestore1">
					Lấy dữ liệu cũ</label
				>
			</div>
		</div>
	</div>
</template>
<script>
import { validateSubdomain } from '@/utils';

export default {
	name: 'Hostname',
	props: ['modelValue', 'checkRestore', 'checkRestore'],
	emits: ['update:modelValue', 'error', 'update:checkRestore'],
	data() {
		return {
			subdomainAvailable: false,
			errorMessage: null
		};
	},
	resources: {
		domain() {
			return {
				url: 'press.api.site.get_domain',
				auto: true
			};
		}
	},
	computed: {
		domain() {
			return this.$resources.domain.data;
		}
	},
	methods: {
		checkRestoreChange(e) {
			this.$emit('update:checkRestore', e.target.value);
		},
		async subdomainChange(e) {
			let subdomain = e.target.value;
			this.$emit('update:modelValue', subdomain);
			this.subdomainAvailable = false;

			let error = this.validateSubdomain(subdomain);
			if (!error) {
				let subdomainTaken = await this.$call('press.api.site.exists', {
					subdomain,
					domain: this.domain
				});
				if (subdomainTaken) {
					error = `${subdomain}.${this.domain} đã tồn tại.`;
				} else {
					this.subdomainAvailable = true;
				}
			}
			this.errorMessage = error;
			this.$emit('error', error);
		},
		validateSubdomain(subdomain) {
			return validateSubdomain(subdomain);
		}
	}
};
</script>
