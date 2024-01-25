<template>
	<div>
		<label class="text-lg font-semibold"> Thông tin khởi tạo tổ chức </label>
		<p class="text-base text-gray-700">
			Thông tin tóm tắt cho việc tạo tổ chức của bạn
		</p>
		<div
			class="mt-2 flex flex-col space-y-2 rounded-md border p-2 text-base leading-5"
		>
			<div><strong>Tên miền: </strong>{{ detail.subdomain }}</div>
			<div>
				<strong>Các ứng dụng đã đăng ký: </strong>
				<div class="ml-6">
					<div v-for="(app, index) in detail.selectedApps" :key="app">
						{{ index + 1 }}. {{ app }} {{ app == 'frappe' ? '(mặc định)' : '' }}
					</div>
				</div>
			</div>
			<div>
				<strong>Máy chủ: </strong>
				<div class="ml-6" v-if="detail?.selectedPlan">
					<div>
						Mức sử dụng: {{ detail.selectedPlan.cpu_time_per_day }}
						{{ $plural(detail.selectedPlan.cpu_time_per_day, 'giờ', 'giờ') }} /
						ngày
					</div>
					<div>
						Database:
						{{ formatBytes(detail.selectedPlan.max_database_usage, 0, 2) }}
					</div>
					<div>
						Ổ cứng:
						{{ formatBytes(detail.selectedPlan.max_storage_usage, 0, 2) }}
					</div>
				</div>
			</div>
			<div class="overflow-x-auto">
				<strong
					>Hóa đơn cần chi trả cho {{ this.$resources.dayRequire.data }} ngày:
				</strong>
				<table v-if="infoInvoice" class="text w-full text-sm">
					<thead>
						<tr class="text-gray-600">
							<th class="border-b py-3 pr-2 text-left font-normal">Mô tả</th>

							<th
								class="whitespace-nowrap border-b py-3 pr-2 text-right font-normal"
							>
								Tỉ lệ
							</th>
							<th class="border-b py-3 pr-2 text-right font-normal">Số tiền</th>
						</tr>
					</thead>
					<tbody>
						<tr v-for="item in infoInvoice.items">
							<td class="border-b py-3 pr-2">{{ item.name }}</td>
							<td class="border-b py-3 pr-2 text-right">
								{{ item.formatter.rate }} x
								{{ this.$resources.dayRequire.data }}
							</td>
							<td class="border-b py-3 pr-2 text-right font-semibold">
								{{ item.formatter.price }} VND
							</td>
						</tr>
					</tbody>
					<tfoot>
						<tr>
							<td></td>
							<td class="pb-2 pr-2 pt-4 text-right font-semibold">Tổng cộng</td>
							<td
								class="whitespace-nowrap pb-2 pr-2 pt-4 text-right font-semibold"
							>
								{{ infoInvoice.formatter.total }} VND
							</td>
						</tr>
					</tfoot>
				</table>
			</div>
		</div>
	</div>
</template>
<script>
export default {
	name: 'SiteSummaryBilling',
	emits: ['update:totalBilling'],
	props: ['detail', 'totalBilling'],
	components: {},
	data() {
		return {};
	},
	mounted() {
		// this.$socket.on('press_job_update', data => {
		// 	console.log(data);
		// });
	},
	unmounted() {
		// this.$socket.off('eval_js', () => {
		// 	console.log('ok2');
		// });
	},
	resources: {
		domain() {
			return {
				url: 'press.api.site.get_domain',
				auto: true
			};
		},
		dayRequire() {
			return {
				url: 'press.api.site.get_day_required_register_site',
				auto: true
			};
		}
	},
	methods: {},
	computed: {
		infoInvoice() {
			let info = this.detail;
			let items = [];
			let total = 0;
			const daysInSeptember = this.$getDays(
				new Date().getFullYear(),
				new Date().getMonth() + 1
			);

			if (info.subdomain) {
				let day_required = this.$resources.dayRequire.data;
				if (info.selectedPlan) {
					let rate = Number.parseFloat(
						(info.selectedPlan?.price_vnd / daysInSeptember).toFixed(2)
					);
					let price = Math.round(rate * day_required);
					total += price;

					items.push({
						name: this.detail.subdomain + '.' + this.$resources.domain.data,
						rate: rate,
						price: price,
						formatter: {
							price: this.$formatMoney(price),
							rate: this.$formatMoney(rate)
						}
					});
				}
				if (info.selectedApps) {
					info.selectedApps.forEach(el => {
						let plan = info.appPlans[el];
						let item = {
							name: el,
							rate: 0,
							price: 0,
							formatter: {
								price: 0,
								rate: 0
							}
						};
						if (plan) {
							let rate = Number.parseFloat((plan / daysInSeptember).toFixed(2));
							let price = Math.round(rate * day_required);
							total += price;
							item = {
								...item,
								rate: rate,
								price: price,
								formatter: {
									price: this.$formatMoney(price),
									rate: this.$formatMoney(rate)
								}
							};
						}
						items.push(item);
					});
				}
				this.$emit('update:totalBilling', total);
			}

			return {
				items: items,
				total: total,
				formatter: {
					total: this.$formatMoney(total)
				}
			};
		}
	},
	watch: {}
};
</script>
