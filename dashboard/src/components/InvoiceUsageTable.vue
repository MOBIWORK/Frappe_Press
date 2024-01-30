<template>
	<div>
		<div v-if="doc" class="overflow-x-auto">
			<table class="text w-full text-sm">
				<thead>
					<tr class="text-gray-600">
						<th class="border-b py-3 pr-2 text-left font-normal">Mô tả</th>
						<th class="border-b py-3 pr-2 text-left font-normal">Tổ chức</th>
						<th
							class="whitespace-nowrap border-b py-3 pr-2 text-right font-normal"
						>
							Tỉ lệ
						</th>
						<th class="border-b py-3 pr-2 text-right font-normal">Số tiền</th>
					</tr>
				</thead>
				<tbody>
					<tr v-for="(row, i) in doc.items" :key="row.idx">
						<td class="border-b py-3 pr-2">
							{{ row.description || row.document_name }}
						</td>
						<td class="border-b py-3 pr-2">
							{{ row.site || '-' }}
						</td>
						<td class="border-b py-3 pr-2 text-right">
							{{ this.$formatMoney(row.rate) }} x {{ row.quantity }}
						</td>
						<td class="border-b py-3 pr-2 text-right font-semibold">
							{{ this.$formatMoney(doc.items[i].amount, 0) }} VND
						</td>
					</tr>
				</tbody>
				<tfoot>
					<tr v-if="doc.total_discount_amount > 0">
						<td></td>
						<td class="pb-2 pr-2 pt-4 text-right font-semibold">
							Tổng số tiền chưa giảm giá
						</td>
						<td
							class="whitespace-nowrap pb-2 pr-2 pt-4 text-right font-semibold"
						>
							{{ doc.formatted.total_before_discount }}
						</td>
					</tr>
					<tr v-if="doc.total_discount_amount > 0">
						<td></td>
						<td class="pb-2 pr-2 pt-4 text-right font-semibold">
							Tổng số tiền đã giảm giá
						</td>
						<td
							class="whitespace-nowrap pb-2 pr-2 pt-4 text-right font-semibold"
						>
							{{
								doc.partner_email && doc.partner_email != doc.team
									? 0
									: doc.formatted.total_discount_amount
							}}
						</td>
					</tr>
					<!-- gst -->
					<tr v-if="doc.gst > 0">
						<td></td>
						<td class="pb-2 pr-2 pt-4 text-right font-semibold">
							Tổng cộng (Chưa tính thuế)
						</td>
						<td
							class="whitespace-nowrap pb-2 pr-2 pt-4 text-right font-semibold"
						>
							{{ doc.formatted.total_before_tax }}
						</td>
					</tr>
					<tr v-if="doc.gst > 0">
						<td></td>
						<td class="pb-2 pr-2 pt-4 text-right font-semibold">
							IGST @ {{ Number($account.billing_info.gst_percentage * 100) }}%
						</td>
						<td
							class="whitespace-nowrap pb-2 pr-2 pt-4 text-right font-semibold"
						>
							{{ doc.formatted.gst }}
						</td>
					</tr>
					<!-- vat -->
					<tr v-if="doc.vat > 0">
						<td></td>
						<td class="pb-2 pr-2 pt-4 text-right font-semibold">
							Tổng cộng (Chưa tính thuế VAT)
						</td>
						<td
							class="whitespace-nowrap pb-2 pr-2 pt-4 text-right font-semibold"
						>
							{{ doc.formatted.total_before_vat }}
						</td>
					</tr>
					<tr v-if="doc.vat > 0">
						<td></td>
						<td class="pb-2 pr-2 pt-4 text-right font-semibold">
							Thuế VAT {{ Number(doc.vat) }}%
						</td>
						<td
							class="whitespace-nowrap pb-2 pr-2 pt-4 text-right font-semibold"
						>
							{{ this.$formatMoney(doc.total - doc.total_before_vat) }} VND
						</td>
					</tr>
					<tr>
						<td></td>
						<td class="pb-2 pr-2 pt-4 text-right font-semibold">
							Tổng tiền thanh toán
						</td>
						<td
							class="whitespace-nowrap pb-2 pr-2 pt-4 text-right font-semibold"
						>
							{{ totalInvoice }}
						</td>
					</tr>
					<template v-if="doc.total !== doc.amount_due && doc.docstatus == 1">
						<tr>
							<td></td>
							<td class="pr-2 text-right">Số dư đã áp dụng:</td>
							<td class="whitespace-nowrap py-3 pr-2 text-right font-semibold">
								- {{ doc.formatted.applied_credits }}
							</td>
						</tr>
						<tr>
							<td></td>
							<td class="pr-2 text-right">Số tiền đến hạn:</td>
							<td class="whitespace-nowrap py-3 pr-2 text-right font-semibold">
								{{ doc.formatted.amount_due }}
							</td>
						</tr>
					</template>
				</tfoot>
			</table>
		</div>
		<div class="py-20 text-center" v-if="$resources.doc.loading">
			<Button :loading="true">Đang tải</Button>
		</div>
	</div>
</template>
<script>
export default {
	name: 'InvoiceUsageTable',
	props: ['invoice', 'invoiceDoc'],
	resources: {
		doc() {
			return {
				url: 'press.api.billing.get_invoice_usage',
				params: { invoice: this.invoice },
				auto: this.invoice,
				onSuccess(doc) {
					this.$emit('doc', doc);
				}
			};
		}
	},
	watch: {
		invoice(value) {
			if (value) {
				this.$resources.doc.fetch();
			}
		}
	},
	computed: {
		totalInvoice() {
			let total =
				this.doc.partner_email && this.doc.partner_email != this.doc.team
					? this.doc.total_before_discount
					: this.doc.total;
			return this.$formatMoney(total, 0) + ' VND';
		},
		doc() {
			return this.invoiceDoc || this.$resources.doc.data;
		}
	}
};
</script>
