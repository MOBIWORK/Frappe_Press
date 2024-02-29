<template>
	<div>
		<label class="text-lg font-semibold">
			{{ $t('SiteSummaryBilling_content_1') }}
		</label>
		<p class="text-base text-gray-700">
			{{ $t('SiteSummaryBilling_content_2') }}
		</p>
		<div
			class="mt-2 flex flex-col space-y-2 rounded-md border p-2 text-base leading-5"
		>
			<div>
				<strong>{{ $t('Domains') }}: </strong>{{ detail.subdomain }}
			</div>
			<div>
				<strong>{{ $t('SiteSummaryBilling_content_3') }}: </strong>
				<div class="ml-6">
					<div v-for="(app, index) in detail.selectedApps" :key="app">
						{{ index + 1 }}. {{ app }}
						{{ app == 'frappe' ? `(${$t('default')})` : '' }}
					</div>
				</div>
			</div>
			<div>
				<strong>{{ $t('Server') }}: </strong>
				<div class="ml-6" v-if="detail?.selectedPlan">
					<div>
						{{ $t('Compute') }}: {{ detail.selectedPlan.cpu_time_per_day }}
						{{
							$plural(
								detail.selectedPlan.cpu_time_per_day,
								$t('hour'),
								$t('hours')
							)
						}}
						/
						{{ $t('day') }}
					</div>
					<div>
						Database:
						{{ formatBytes(detail.selectedPlan.max_database_usage, 0, 2) }}
					</div>
					<div>
						{{ $t('Disk') }}:
						{{ formatBytes(detail.selectedPlan.max_storage_usage, 0, 2) }}
					</div>
				</div>
			</div>
			<div class="overflow-x-auto">
				<strong
					>{{ $t('SiteSummaryBilling_content_4') }}
					{{ this.$resources.dayRequire.data }}
					{{ $plural(this.$resources.dayRequire.data, $t('day'), $t('days')) }}:
				</strong>
				<table v-if="infoInvoice" class="text w-full text-sm">
					<thead>
						<tr class="text-gray-600">
							<th class="border-b py-3 pr-2 text-left font-normal">
								{{ $t('description') }}
							</th>

							<th
								class="whitespace-nowrap border-b py-3 pr-2 text-right font-normal"
							>
								{{ $t('rate') }}
							</th>
							<th class="border-b py-3 pr-2 text-right font-normal">
								{{ $t('amount_of_money') }}
							</th>
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
							<td class="pb-2 pr-2 pt-4 text-right font-semibold">
								{{ $t('invoiceusagetable_content_2') }}
							</td>
							<td
								class="whitespace-nowrap pb-2 pr-2 pt-4 text-right font-semibold"
							>
								{{ infoInvoice.formatter.total_befor_tax }} VND
							</td>
						</tr>
						<tr>
							<td></td>
							<td class="pb-2 pr-2 pt-4 text-right font-semibold">
								{{ $t('vat_tax') }} {{ Number($resources.vat.data) }}%
							</td>
							<td
								class="whitespace-nowrap pb-2 pr-2 pt-4 text-right font-semibold"
							>
								{{ infoInvoice.formatter.fee_vat }} VND
							</td>
						</tr>
						<tr>
							<td></td>
							<td class="pb-2 pr-2 pt-4 text-right font-semibold">
								{{ $t('total_payment_amount') }}
							</td>
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
		vat() {
			return {
				url: 'press.api.site.get_vat_upcoming_invoice',
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
	computed: {
		infoInvoice() {
			let info = this.detail;
			let items = [];
			let total = 0;
			let total_befor_tax = 0;
			let fee_vat = 0;
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
					total_befor_tax += price;

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
							total_befor_tax += price;
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
				fee_vat = Math.round(
					(total_befor_tax * this.$resources.vat.data) / 100
				);
				total = total_befor_tax + fee_vat;
				this.$emit('update:totalBilling', total);
			}

			return {
				items: items,
				total_befor_tax: total_befor_tax,
				fee_vat: fee_vat,
				total: total,
				formatter: {
					total_befor_tax: this.$formatMoney(total_befor_tax),
					fee_vat: this.$formatMoney(fee_vat),
					total: this.$formatMoney(total)
				}
			};
		}
	}
};
</script>
