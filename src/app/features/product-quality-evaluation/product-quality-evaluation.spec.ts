import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ProductQualityEvalution } from './product-quality-evaluation';

describe('ProductQualityEvalution', () => {
  let component: ProductQualityEvalution;
  let fixture: ComponentFixture<ProductQualityEvalution>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ProductQualityEvalution],
    }).compileComponents();

    fixture = TestBed.createComponent(ProductQualityEvalution);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
